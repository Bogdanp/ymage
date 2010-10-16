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
import os

from gui import Slideshow
from optparse import OptionParser
from pyglet import app

def parse_options():
    parser = OptionParser(
        usage="usage: %prog [OPTIONS] PATH",
        version="%prog 0.2"
    )
    parser.add_option(
        "-d", "--duration",
        help="the duration of a single slide [default: %default]",
        dest="duration",
    )
    parser.add_option(
        "-i", "--index",
        help="start with slide number INDEX [default: %default]",
        dest="index",
    )
    parser.add_option(
        "-l", "--last-index",
        help="start with the slide last viewed in PATH",
        dest="last_index", action="store_true",
    )
    parser.add_option(
        "-w", "--windowed",
        help="start ymage in windowed mode",
        dest="windowed", action="store_true",
    )
    parser.set_defaults(
        duration=5, index=1,
        last_index=False,
        windowed=False,
    )

    options, args = parser.parse_args()

    try:
        options.path = args[0]
        options.save_file = os.path.join(args[0], ".ymage")
    except IndexError:
        parser.error("you must specify a PATH")

    return options

def get_paths(path):
    types = ["bmp", "jpg", "jpeg", "png"]
    paths = []

    for root, dirs, files in os.walk(path):
        for _file in files:
            for _type in types:
                if _file.endswith(_type):
                    paths.append(os.path.join(root, _file))

    return sorted(paths)

def main():
    options = parse_options()
    paths = get_paths(options.path)
    slideshow = Slideshow(options, paths)

    app.run()

    try:
        open(options.save_file, "w").write(str(slideshow.index))
    except IOError:
        pass

    return 0
