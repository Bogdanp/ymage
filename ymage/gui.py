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
from pyglet import app, gl, text, window

from ymage.helpers import reschedule, reschedule_once
from ymage.slideshow import Slideshow

# List of characters from 0 to 9 and A to Z
ALPHANUM = [chr(c) for c in range(48, 58)] + [chr(c) for c in range(65, 91)]

class Printer(text.Label):
    def __init__(self):
        super(Printer, self).__init__(
            "", "Arial", 12, False, False,
            (0, 255, 0, 255), 10, 10
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
                window.key.PERIOD: ".",
                window.key.MINUS: "-",
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

class Window(window.Window):
    def __init__(self, options):
        super(Window, self).__init__(
            800, 600, "Loading...", True, None, False
        )

        self.slideshow = Slideshow(options)
        self.options = options
        self.printer = Printer()
        self.reader = Reader(self.printer)
        self.setup()

    def setup(self):
        if not self.options.windowed:
            self.toggle_fullscreen()

    def search(self, query=None):
        if query is None:
            self.reader.start_reading("Search for: ", self.search)
        else:
            self.slideshow.display(action="search", query=query)

    def jump(self, index=None):
        if index is None:
            self.reader.start_reading("Slide: ", self.jump)
        else:
            self.slideshow.display(action="jump", index=index)

    def toggle_fullscreen(self):
        self.activate()
        self.set_mouse_visible(self.fullscreen)
        self.set_fullscreen(not self.fullscreen)

    def update_caption(self):
        self.set_caption("ymage [%d/%d]" % (
            self.slideshow.index + 1, len(self.slideshow.slides)
        ))

    def on_draw(self):
        self.clear()

        try:
            self.slideshow.draw_slide(self.width, self.height)
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
                window.key.D: lambda: self.reader.start_reading("Duration: ", self.slideshow.set_duration),
                window.key.P: lambda: self.printer._print(self.slideshow.get_current()),
                window.key.R: lambda: self.slideshow.display(action="random", previous=False),
                window.key.E: lambda: self.slideshow.display(action="random", previous=True),
                window.key.UP: lambda: self.printer._print("Duration: " + self.slideshow.increase_duration()),
                window.key.DOWN: lambda: self.printer._print("Duration: " + self.slideshow.decrease_duration()),
                window.key.LEFT: lambda: self.slideshow.display(action="prev"),
                window.key.RIGHT: lambda: self.slideshow.display(action="next"),
                window.key.SPACE: lambda: self.printer._print(self.slideshow.toggle_paused()),
                window.key.I: self.jump,
                window.key.F: self.toggle_fullscreen,
                window.key.SLASH: self.search,
                window.key.ESCAPE: app.exit,
            }[symbol]()
        except KeyError:
            pass
