# Copyright (c) 2014 Bogdan Popa
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
from pyglet import gl, clock


class Transition(object):
    transitions = {
        "simple": "TransitionSimple",
        "blend": "TransitionBlend"
    }

    @classmethod
    def create(self, slideshow):
        trans_class = TransitionSimple
        try:
            trans_class = globals()[self.transitions[slideshow.options.transition]]
        except KeyError:
            pass
        return trans_class(slideshow)

    def __init__(self, slideshow):
        self.slideshow = slideshow
        self.queue = []

    def setup(self):
        pass

    def in_transition(self):
        for index, transition in enumerate(self.queue):
            if transition["phase"] == 0:
                del self.queue[index]

        if len(self.queue) <= 0:
            clock.unschedule(self.tick)

        return len(self.queue) > 0

    def add_transition(self, previous, next):
        self.queue.append({
            "previous": previous,
            "next": next,
            "phase": 1.,
        })
        clock.schedule_interval(self.tick, 1.0 / 30)

    def tick(self, dt):
        self.queue[0]["phase"] -= dt / self.slideshow.options.transition_duration
        self.queue[0]["phase"] = max([0, self.queue[0]["phase"]])

    def draw(self, width, height):
        pass


class TransitionSimple(Transition):
    def __init__(self, *args, **kwargs):
        Transition.__init__(self, *args, **kwargs)

    def add_transition(self, previous, next):
        pass


class TransitionBlend(Transition):
    def __init__(self, *args, **kwargs):
        Transition.__init__(self, *args, **kwargs)

    def setup(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_CONSTANT_ALPHA, gl.GL_ONE)
        gl.glBlendColor(0.0, 0.0, 0.0, 1.0)

    def draw(self, width, height):
        transition = self.queue[0]
        gl.glBlendColor(0.0, 0.0, 0.0, transition["phase"])
        self.slideshow.draw_slide(width, height, transition["previous"])
        gl.glBlendColor(0.0, 0.0, 0.0, 1.0 - transition["phase"])
        self.slideshow.draw_slide(width, height, transition["next"])
