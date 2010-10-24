# Copyright (c) 2010 Bogdan Popa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import division

from pyglet import image
from random import randint

from ymage.helpers import reschedule, reschedule_once

class Slideshow(object):
    def __init__(self, options):
        self.options = options
        self.slide = None
        self.setup()
        self.display(action="none")

    def setup(self):
        if self.options.last_index:
            try:
                self.index = int(open(self.options.save_file).read())
            except (IOError, ValueError):
                self.index = 0
        else:
            self.index = self.options.index - 1

        self.options.duration = float(self.options.duration)
        self.options.paused = False
        self.randoms = []
        self.rindex = 0
        self.slides = self.options.paths

    def get_current(self):
        return self.slides[self.index]

    def decrease_duration(self):
        self.options.duration -= 0.5

        if self.options.duration < 0:
            self.options.duration = 0

        self.display(action="reschedule")
        return str(self.options.duration)

    def increase_duration(self):
        self.options.duration += 0.5
        self.display(action="reschedule")
        return str(self.options.duration)

    def set_duration(self, n):
        try:
            self.options.duration = abs(float(n))
            self.display(action="reschedule")
        except ValueError:
            pass

    def toggle_paused(self):
        self.options.paused = not self.options.paused
        return "Paused" if self.options.paused else "Unpaused"

    def prev(self):
        self.index -= 1

        if self.index < 0:
            self.index = len(self.slides) - 1

    def next(self):
        self.index += 1

        if self.index >= len(self.slides):
            self.index = 0

    def jump(self, index):
        try:
            index = int(index) - 1

            if index >= 0 and index < len(self.slides):
                self.index = index
        except ValueError:
            pass

    def random(self, previous):
        if previous:
            self.rindex -= 1

            if self.rindex < 0:
                self.rindex = len(self.randoms) - 1
        else:
            self.rindex = len(self.randoms)
            self.randoms.append(randint(0, len(self.slides) - 1))

        try:
            self.index = self.randoms[self.rindex]
        except IndexError:
            pass

    def search(self, query):
        for i, slide in enumerate(self.slides):
            if slide.lower().find(query) != -1:
                self.index = i
                return

    def save_last(self):
        try:
            with open(self.options.save_file, "w") as f:
                f.write(str(self.index))
        except IOError:
            pass

    def draw_slide(self, window_width, window_height):
        image_ratio = self.slide.width / self.slide.height
        window_ratio = window_width / window_height

        if image_ratio > window_ratio:
            image_width = window_width
            image_height = window_width / image_ratio
        else:
            image_width = window_height * image_ratio
            image_height = window_height

        padding_left = (window_width - image_width) / 2
        padding_bottom = (window_height - image_height) / 2
        self.slide.blit(
            padding_left, padding_bottom, 0,
            image_width, image_height
        )

    def display(self, dt=None, action="next", *args, **kwargs):
        if not self.options.paused or dt is None:
            # dt == None => we got here by way of
            # a key press and not the clock so it's
            # okay to switch to a different slide
            try:
                {
                    "prev": self.prev,
                    "next": self.next,
                    "jump": lambda: self.jump(kwargs["index"]),
                    "none": lambda: None,
                    "random": lambda: self.random(kwargs["previous"]),
                    "search": lambda: self.search(kwargs["query"]),
                }[action]()
            except KeyError:
                pass

        if action != "reschedule":
            self.save_last()
            self.slide = image.load(self.slides[self.index])

        reschedule(self.display, self.options.duration)
