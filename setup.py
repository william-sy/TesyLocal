import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tesylocal",
    version = "1.2",
    author = "William",
    author_email = "wvanbeek.sy@gmail.com",
    description = ("Connect to a Tesy Boiler without the use of the modeco cloud."),
    license = "GPL-3.0-only",
    keywords = ["Tesy", "Modeco", "Local"],
    url = "https://github.com/william-sy/TesyLocal",
    packages=['tesylocal'],
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=['websocket-client', 'dpath', 'ipaddress'],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
    ],
)
