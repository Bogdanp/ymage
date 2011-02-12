# Copyright (c) 2011 Bogdan Popa
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
        self.setup()
        self.display(action="none")

    def setup(self):
        try:
            if self.options.last_index:
                with open(self.options.save_file) as file_:
                    self.index = int(file_.read())
            else:
                self.index = int(self.options.index) - 1
        except (IOError, ValueError):
            self.index = 0
        try:
            self.options.duration = float(self.options.duration)
        except ValueError:
            self.options.duration = 5
        self.options.paused = False
        self.randoms = []
        self.rindex = 0
        self.slides = self.options.paths
        self.slide = None

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

    def previous(self):
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

    def draw_slide(self, window_w, window_h):
        image_ratio = self.slide.width / self.slide.height
        window_ratio = window_w / window_h
        if image_ratio > window_ratio:
            image_w = window_w
            image_h = window_w / image_ratio
        else:
            image_w = window_h * image_ratio
            image_h = window_h
        image_x = (window_w - image_w) / 2
        image_y = (window_h - image_h) / 2
        self.slide.blit(
            x=image_x, y=image_y,
            width=image_w, height=image_h
        )

    def display(self, dt=None, action="next", *args, **kwargs):
        if not self.options.paused or dt is None:
            # dt == None => we got here by way of
            # a key press and not the clock so it's
            # okay to switch to a different slide
            # when paused.
            try:
                {
                    "previous": self.previous,
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
