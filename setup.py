import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tesylocal",
    version = "1.0",
    author = "William",
    author_email = "None",
    description = ("Connect to a Tesy Boiler ithout the use of the cloud."),
    license = "GPL-3.0-only",
    keywords = "Tesy",
    url = "",
    packages=['tesy'],
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=['websocket-client', 'dpath', 'ipaddress'],
    classifiers=[
        "Topic :: Utilities",
        "License :: GPL-3.0-only",
    ],
)
