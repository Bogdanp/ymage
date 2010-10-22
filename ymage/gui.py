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
        super(Printer, self).__init__(
            font_name="Arial", font_size=12,
            color=(0, 255, 0, 255),
            x=10, y=10,
        )

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
        self.input = ""

    def read(self, symbol, modifiers):
        self.is_reading = True

        if symbol == window.key.RETURN:
            self.printer.clear()
            self.toggle_reading()
            self.callback(self.input)
            return
        elif symbol == window.key.ESCAPE:
            self.printer.clear()
            self.toggle_reading()
            return
        elif symbol == window.key.BACKSPACE:
            self.input = self.input[:-1]

        try:
            self.input += {
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
                self.input += representation
            else:
                self.input += representation.lower()

        self.printer._print(self.message + self.input + "_")

    def start_reading(self, message, callback):
        self.callback = callback
        self.message = message
        self.input = ""
        self.printer._print(self.message + "_")
        self.toggle_reading()

    def toggle_reading(self):
        self.is_reading = not self.is_reading

class Slide(object):
    def __init__(self, path):
        self.image = None
        self.path = path

    def draw(self, window_width, window_height):
        if self.image is None:
            self.image = image.load(self.path)

        image_ratio = self.image.width / self.image.height
        window_ratio = window_width / window_height

        if image_ratio > window_ratio:
            image_height = window_width / image_ratio
            image_width = window_width
        else:
            image_height = window_height
            image_width = window_height * image_ratio

        padding_left = (window_width - image_width) / 2
        padding_bottom = (window_height - image_height) / 2

        self.image.blit(
            padding_left, padding_bottom, 0,
            image_width, image_height
        )

class Slideshow(object):
    def __init__(self, options):
        self.options = options
        self.slides = []
        self.setup()
        self.display(action="none")

    def setup(self):
        for path in self.options.paths:
            self.slides.append(Slide(path))

        if self.options.last_index:
            try:
                self.index = int(open(self.options.save_file).read())
            except (IOError, ValueError):
                self.index = 0
        else:
            self.index = self.options.index

        self.options.duration = float(self.options.duration)
        self.options.paused = False
        self.randoms = []
        self.rindex = 0

    def get_current(self):
        return self.slides[self.index]

    def decrease_duration(self):
        self.options.duration -= 0.5

        if self.options.duration < 0:
            self.options.duration = 0

        self.display(action="none")

    def increase_duration(self):
        self.options.duration += 0.5
        self.display(action="none")

    def set_duration(self, n):
        self.options.duration = abs(n)
        self.display(action="none")

    def toggle_paused(self):
        self.options.paused = not self.options.paused

    def prev(self):
        self.index -= 1

        if self.index < 0:
            self.index = len(self.slides) - 1

    def next(self):
        self.index += 1

        if self.index >= len(self.slides):
            self.index = 0

    def jump(self, index):
        index -= 1

        if index > 0 and index < len(self.slides):
            self.index = index

    def search(self, query, direction):
        start = {
            "backward": 0,
            "forward": self.index,
        }[direction]

        for i, slide in enumerate(self.slides[start:], start):
            if slide.path.lower().find(query) != -1:
                self.index = i
                return

    def random(self, previous):
        if previous:
            self.rindex -= 1

            if self.rindex < 0:
                self.rindex = len(self.randoms) - 1
        else:
            self.rindex = len(self.randoms)
            self.randoms.append(random.randint(0, len(self.slides)))

        try:
            self.index = self.randoms[self.rindex]
        except IndexError:
            pass

    def display(self, dt=None, action="next", *args, **kwargs):
        if not self.options.paused or dt is None:
            # dt == None => we got here by way of
            # a key press and not the clock so it's
            # okay to switch to a different slide
            {
                "prev": self.prev,
                "next": self.next,
                "jump": lambda: self.jump(kwargs["index"]),
                "none": lambda: None,
                "random": lambda: self.random(kwargs["previous"]),
                "search": lambda: self.search(kwargs["query"], kwargs["direction"]),
            }[action]()

        reschedule(self.display, self.options.duration)

class Window(window.Window):
    def __init__(self, options):
        super(Window, self).__init__(
            fullscreen=False, resizable=True,
        )

        self.slideshow = Slideshow(options)
        self.options = options
        self.printer = Printer()
        self.reader = Reader(self.printer)
        self.setup()

    def setup(self):
        if not self.options.windowed:
            self.toggle_fullscreen()

    def toggle_fullscreen(self):
        self.activate()
        self.set_mouse_visible(self.fullscreen)
        self.set_fullscreen(not self.fullscreen)

    def update_caption(self):
        pass

    def on_draw(self):
        self.clear()

        try:
            self.slideshow.get_current().draw(self.width, self.height)
        except gl.lib.GLException:
            # In case one of the slides is corrupted
            # move on to the next
            self.slideshow.display()

        self.update_caption()
        self.printer.draw()

    def on_key_press(self, symbol, modifiers):
        if self.reader.is_reading:
            self.reader.read(symbol, modifiers)
            return

        try:
            {
                window.key.D: lambda: self.reader.read("Duration: ", self.slideshow.set_duration),
                window.key.I: lambda: self.reader.read("Index: ", self.slideshow.jump),
                window.key.P: lambda: self.printer._print(self.slideshow.get_current().path),
                window.key.R: lambda: self.slideshow.display(action="random", previous=False),
                window.key.E: lambda: self.slideshow.display(action="random", previous=True),
                window.key.LEFT: lambda: self.slideshow.display(action="previous"),
                window.key.RIGHT: lambda: self.slideshow.display(action="next"),
                window.key.SLASH: lambda: self.slideshow.display(action="search", direction="forward"),
                window.key.QUESTION: lambda: self.slideshow.display(action="search", direction="backward"),
                window.key.F: self.toggle_fullscreen,
                window.key.UP: self.slideshow.increase_duration,
                window.key.DOWN: self.slideshow.decrease_duration,
                window.key.SPACE: self.slideshow.toggle_paused,
                window.key.ESCAPE: app.exit,
            }[symbol]()
        except KeyError:
            pass
