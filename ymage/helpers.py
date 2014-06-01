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
import os

from pyglet import clock

def reschedule(callback, interval, *args, **kwargs):
    clock.unschedule(callback)
    clock.schedule_interval(callback, interval, *args, **kwargs)

def reschedule_once(callback, interval, *args, **kwargs):
    clock.unschedule(callback)
    clock.schedule_once(callback, interval, *args, **kwargs)

def valid_type(file_):
    types = ("bmp", "jpg", "jpeg", "png", "tif", "tiff")
    for type_ in types:
        if file_.lower().endswith(type_):
            return True
    return False

def get_files(path):
    for root, dirs, files in os.walk(path):
        for file_ in files:
            if valid_type(file_):
                yield os.path.join(root, file_)

def get_paths(path):
    paths = []
    for file_ in get_files(path):
        paths.append(file_)
    return sorted(paths)
