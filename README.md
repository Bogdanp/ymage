ymage
-----
ymage is a simple image slideshow creator written in Python. Here's a [screenshot](http://imgur.com/h3IHG.jpg).

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

Sample usage
------------
* Start in windowed mode: `ymage -w /path/to/your/pictures/folder`
* Start at the 10th slide: `ymage -i 10 /path/to/your/pictures/folder`
* Start in windowed mode with a 20 second duration per slide: `ymage -w -d 20 /path/to/your/pictures/folder`

Keybidings
----------
* __/__: Search for a certain image (searches through the paths for your query)
* __d__: Set duration
* __f__: Toggle fullscreen mode
* __i__: Jump to a slide
* __p__: Print the path of the current image
* __e__: Jump to previous random slide
* __r__: Jump to a random slide
* __←__: Previous slide
* __→__: Next slide
* __↑__: Increase duration
* __↓__: Decrease duration
* __SPC__: Toggle paused
* __ESC__: Exit ymage
