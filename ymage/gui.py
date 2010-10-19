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

# List of characters from 0 to 9 and A to Z
ALPHANUM = [chr(c) for c in range(48, 58)] + [chr(c) for c in range(65, 91)]

def reschedule(callback, interval, *args, **kwargs):
    clock.unschedule(callback)
    clock.schedule_interval(callback, interval, *args, **kwargs)

def reschedule_once(callback, interval, *args, **kwargs):
    clock.unschedule(callback)
    clock.schedule_once(callback, interval, *args, **kwargs)

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

class Reader(object):
    def __init__(self, printer):
        self.is_reading = False
        self.callback = None
        self.printer = printer
        self.message = ""
        self._input = ""

    def read(self, symbol, modifiers):
        self.is_reading = True

        if symbol == window.key.RETURN:
            self.printer.clear()
            self.toggle_reading()
            self.callback(self._input)
            return
        elif symbol == window.key.ESCAPE:
            self.printer.clear()
            self.toggle_reading()
            return
        elif symbol == window.key.BACKSPACE:
            self._input = self._input[:-1]

        try:
            self._input += {
                window.key.MINUS: "-",
                window.key.PERIOD: ".",
                window.key.SPACE: " ",
            }[symbol]
        except KeyError:
            pass

        representation = window.key.symbol_string(symbol)
        representation = representation.replace("_", "")

        if representation in ALPHANUM:
            if modifiers & window.key.MOD_SHIFT:
                self._input += representation
            else:
                self._input += representation.lower()

        self.printer._print(self.message + self._input + "_")

    def start_reading(self, message, callback):
        self.callback = callback
        self.message = message
        self._input = ""

        self.printer._print(self.message + "_")
        self.toggle_reading()

    def toggle_reading(self):
        self.is_reading = not self.is_reading

class Slideshow(window.Window):
    def __init__(self, options):
        super(Slideshow, self).__init__(
            fullscreen=False, resizable=True,
        )

        self.setup_defaults(options)

        self.duration = float(options.duration)
        self.printer = Printer()
        self.reader = Reader(self.printer)
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

    def setup_defaults(self, options):
        if not options.windowed:
            self.toggle_fullscreen()

        if options.last_index:
            try:
                self.index = int(open(options.save_file).read())
            except IOError:
                self.index = 0
        else:
            self.index = int(options.index) - 1

    def update_caption(self):
        self.set_caption("ymage [%d/%d]" % (self.index + 1, len(self.paths)))

    def update_duration(self, n=None):
        if not n:
            self.reader.start_reading("Duration: ", self.update_duration)
        else:
            try:
                old_duration = self.duration
                self.duration = float(n)
            except ValueError:
                self.duration = old_duration

    def update_duration_by(self, n):
        self.duration += n

        self.printer._print("Duration: %.1f" % self.duration)
        reschedule(self.update_index_by, self.duration, 1)

    def update_index(self, n=None):
        if not n:
            self.reader.start_reading("Jump to slide: ", self.update_index)
        else:
            try:
                old_index = self.index
                self.index = int(n) - 1
                self.update_index_by(n=0)
            except (IndexError, ValueError):
                self.index = old_index
                self.update_index_by(n=0)

    def update_index_by(self, dt=None, n=1):
        if not self.paused or dt is None:
            self.index += n

            if self.index > len(self.paths) - 1:
                self.index = self.index - len(self.paths)
            elif self.index < 0:
                self.index = len(self.paths) - self.index - 2

        self.slide = image.load(self.paths[self.index])

        self.update_caption()
        reschedule(self.update_index_by, self.duration)

    def update_random_index(self):
        self.index = randint(0, len(self.paths) - 1)

        self.update_index_by(n=0)

    def search_backward(self, query=None):
        if not query:
            self.reader.start_reading("Search backward for image: ", self.search_backward)
        else:
            for i, path in enumerate(self.paths[:self.index]):
                if path.lower().find(query.lower()) != -1:
                    self.index = i
                    self.update_index_by(n=0)
                    break

    def search_forward(self, query=None):
        if not query:
            self.reader.start_reading("Search forward for image: ", self.search_forward)
        else:
            for i, path in enumerate(self.paths[self.index:], self.index):
                if path.lower().find(query.lower()) != -1:
                    self.index = i
                    self.update_index_by(n=0)
                    break

    def toggle_fullscreen(self):
        self.activate()
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
            self.update_index_by(n=1)

        self.printer.draw()

    def on_key_press(self, symbol, modifiers):
        if self.reader.is_reading:
            self.reader.read(symbol, modifiers)
            return

        try:
            {
                window.key.D: self.update_duration,
                window.key.F: self.toggle_fullscreen,
                window.key.I: self.update_index,
                window.key.P: self.print_current_path,
                window.key.R: self.update_random_index,
                window.key.LEFT: lambda: self.update_index_by(n=-1),
                window.key.RIGHT: lambda: self.update_index_by(n=1),
                window.key.UP: lambda: self.update_duration_by(0.5),
                window.key.DOWN: lambda: self.update_duration_by(-0.5),
                window.key.QUESTION: self.search_backward,
                window.key.SLASH: self.search_forward,
                window.key.SPACE: self.toggle_paused,
                window.key.ESCAPE: app.exit,
            }[symbol]()
        except KeyError:
            pass
