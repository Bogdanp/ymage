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
from pyglet import app, gl, graphics, text, window
from string import ascii_letters, digits

from ymage.helpers import reschedule, reschedule_once
from ymage.slideshow import Slideshow

class Printer(text.Label):
    def __init__(self):
        super(Printer, self).__init__(
            "", "monospace", 9, False, False,
            (0, 0, 0, 255), 10, 10
        )

    def draw(self):
        if self.text:
            width, height = len(self.text) * 7 + 20, 30
            graphics.draw(4, gl.GL_QUADS,
                ("v2f", (0, 0, 0, height, width, height, width, 0)),
                ("c4f", (1, 1, 1, 1) * 4)
            )
        super(Printer, self).draw()

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
                window.key.PERIOD: ".",
                window.key.MINUS: "-",
                window.key.SPACE: " ",
            }[symbol]
        except KeyError:
            pass
        representation = window.key.symbol_string(symbol)
        representation = representation.replace("_", "")
        if representation in ascii_letters + digits:
            if modifiers & window.key.MOD_SHIFT:
                self._input += representation
            else:
                self._input += representation.lower()
        self.printer._print(
            "%s: %s_" % (self.message, self._input)
        )

    def start_reading(self, message, callback):
        self.callback = callback
        self.message = message
        self._input = ""
        self.printer._print(
            "%s: _" % self.message
        )
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

    def toggle_fullscreen(self):
        self.activate()
        self.set_mouse_visible(self.fullscreen)
        self.set_fullscreen(not self.fullscreen)

    def update_caption(self):
        self.set_caption("ymage [%d/%d]" % (
            self.slideshow.index + 1, len(self.slideshow.slides)
        ))

    # Actions
    def _set_duration(self):
        self.reader.start_reading(
            "Duration", self.slideshow.set_duration
        )

    def _increase_duration(self):
        self.printer._print("Duration: {}".format(
            self.slideshow.increase_duration()
        ))

    def _decrease_duration(self):
        self.printer._print("Duration: {}".format(
            self.slideshow.decrease_duration()
        ))

    def _previous_slide(self):
        self.slideshow.display(action="previous")

    def _next_slide(self):
        self.slideshow.display(action="next")

    def _toggle_paused(self):
        self.printer._print(
            self.slideshow.toggle_paused()
        )

    def _random(self):
        self.slideshow.display(action="random", previous=False)

    def _previous_random(self):
        self.slideshow.display(action="random", previous=True)

    def _print_info(self):
        self.printer._print("{} [{}/{}]".format(
            self.slideshow.get_current(),
            self.slideshow.index + 1,
            len(self.slideshow.slides)
        ))

    def _search(self, query=None):
        if query is None:
            self.reader.start_reading("Search for", self._search)
        else:
            self.slideshow.display(action="search", query=query)

    def _jump(self, index=None):
        if index is None:
            self.reader.start_reading("Slide", self._jump)
        else:
            self.slideshow.display(action="jump", index=index)

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
                window.key.P: self._print_info,
                window.key.R: self._random,
                window.key.E: self._previous_random,
                window.key.D: self._set_duration,
                window.key.UP: self._increase_duration,
                window.key.DOWN: self._decrease_duration,
                window.key.LEFT: self._previous_slide,
                window.key.RIGHT: self._next_slide,
                window.key.SPACE: self._toggle_paused,
                window.key.I: self._jump,
                window.key.F: self.toggle_fullscreen,
                window.key.SLASH: self._search,
                window.key.RETURN: app.exit,
                window.key.ESCAPE: app.exit,
            }[symbol]()
        except KeyError:
            pass
