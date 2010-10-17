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
from pyglet import app, clock, gl, image, text, window
from random import randint

def reschedule(callback, interval, *args):
    clock.unschedule(callback)
    clock.schedule_interval(callback, interval, *args)

def reschedule_once(callback, interval, *args):
    clock.unschedule(callback)
    clock.schedule_once(callback, interval, *args)

class Printer(text.Label):
    def __init__(self):
        super(Printer, self).__init__()

        self.font_name = "Arial"
        self.font_size = 12
        self.color = (0, 255, 0, 255)
        self.x = 10
        self.y = 10

    def _print(self, message, duration=5):
        self.text = message

        reschedule_once(self.clear, duration)

    def clear(self, dt=None):
        self.text = ""

class Slideshow(window.Window):
    def __init__(self, options):
        super(Slideshow, self).__init__(
            fullscreen=False,
            resizable=True,
        )

        if not options.windowed:
            self.toggle_fullscreen()

        if options.last_index:
            try:
                self.index = int(open(options.save_file).read())
            except IOError:
                self.index = 0
        else:
            self.index = int(options.index) - 1

        self.duration = float(options.duration)
        self.printer = Printer()
        self.paused = False
        self.paths = options.paths
        self.slide = image.load(self.paths[self.index])

        self.update_caption()
        reschedule(self.update_index_by, self.duration)

    def draw_slide(self):
        slide_ratio = self.slide.width / self.slide.height
        screen_ratio = self.screen.width / self.screen.height

        if slide_ratio > screen_ratio:
            slide_width = self.width
            slide_height = self.width / slide_ratio
        else:
            slide_height = self.height
            slide_width = self.height * slide_ratio

        padding_left = (self.width - slide_width) / 2
        padding_top = (self.height - slide_height) / 2

        self.slide.blit(
            padding_left, padding_top,
            width=slide_width, height=slide_height
        )

    def print_current_path(self):
        self.printer._print(self.paths[self.index])

    def update_caption(self):
        self.set_caption("ymage [%d/%d]" % (self.index + 1, len(self.paths)))

    def update_duration_by(self, n):
        self.duration += n

        self.printer._print("Duration: %.1f" % self.duration)
        reschedule(self.update_index_by, self.duration, 1)

    def update_index_by(self, dt=None, n=1):
        if not self.paused or dt is None:
            self.index += n

        if self.index > len(self.paths) - 1:
            self.index = self.index - len(self.paths)
        elif self.index < 0:
            self.index = len(self.paths) - self.index - 2

        self.slide = image.load(self.paths[self.index])

        self.printer.clear()
        self.update_caption()
        reschedule(self.update_index_by, self.duration)

    def update_random_index(self):
        self.index = randint(0, len(self.paths) - 1)

        self.update_index_by(None, 0)

    def toggle_fullscreen(self):
        self.set_mouse_visible(self.fullscreen)
        self.set_fullscreen(not self.fullscreen)

    def toggle_paused(self):
        self.paused = not self.paused

        if self.paused:
            self.printer._print("Paused")
        else:
            self.printer._print("Unpaused")

    def on_draw(self):
        self.clear()

        try:
            self.draw_slide()
        except gl.lib.GLException:
            # In case one of the slides is corrupted
            # move on to the next
            self.update_index_by(None, 1)

        self.printer.draw()

    def on_key_press(self, symbol, modifiers):
        try:
            {
                window.key.F: self.toggle_fullscreen,
                window.key.R: self.update_random_index,
                window.key.P: self.print_current_path,
                window.key.LEFT: lambda: self.update_index_by(None, -1),
                window.key.RIGHT: lambda: self.update_index_by(None, 1),
                window.key.UP: lambda: self.update_duration_by(0.5),
                window.key.DOWN: lambda: self.update_duration_by(-0.5),
                window.key.SPACE: self.toggle_paused,
                window.key.ESCAPE: app.exit
            }[symbol]()
        except KeyError:
            pass
