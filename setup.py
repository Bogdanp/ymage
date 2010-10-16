from setuptools import setup

setup(
    name="ymage",
    version="0.1",
    description="Turns folders into slideshows",
    author="Bogdan Popa",
    author_email="popa.bogdanp@gmail.com",
    url="http://github.com/Bogdanp/ymage",
    packages=["ymage"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python"
    ],
    install_requires=[
        "pyglet>=1.1"
    ],
    entry_points={
        "console_scripts": ["ymage = ymage.ymage:main"]
    }
)
