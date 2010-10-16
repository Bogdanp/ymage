ymage
-----
ymage is a simple image slideshow creator written in Python.

Requirements
------------
ymage requires:

* [Python](http://python.org) 2.5 or later
* [Pyglet](http://pyglet.org) 1.1 or later 

Installation
------------
With [setuptools](http://pypi.python.org/pypi/setuptools) installed run `easy_install ymage` or
grab the latest stable version from [http://github.com/Bogdanp/ymage/](http://github.com/Bogdanp/ymage/),
unpack it and run `python setup.py install`. You can now run ymage from anywhere with `ymage`.

Screenshots
-----------
* [Safe for work](http://imgur.com/h3IHG.jpg)
* [Not safe for work](http://imgur.com/hO9hB.jpg)

Sample usage
------------
* Start in windowed mode: `ymage -w /path/to/your/pictures/folder`
* Start at the 10th slide: `ymage -i 10 /path/to/your/pictures/folder`
* Start in windowed mode with a 20 second duration per slide: `ymage -w -d 20 /path/to/your/pictures/folder`

Keybidings
----------
* __f__: Toggle fullscreen mode
* __p__: Print the path of the current image 
* __r__: Jump to a random slide
* __left arrow__: Previous slide
* __right arrrow__: Next slide
* __up arrow__: Increase duration
* __down arrow__: Decrease duration
* __space__: Toggle paused
* __escape__: Exit ymage 
