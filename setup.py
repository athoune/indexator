#!/usr/bin/env python

"""Setup script for the pyparsing module distribution."""
from distutils.core import setup

from indexator import __version__

setup(# Distribution meta-data
    name = "indexator",
    version = __version__,
    description = "Index",
    author = "Mathieu Lecarme",
    author_email = "mathieu@garambrogne.net",
    url = "http://github.com/athoune/indexator/tree/master",
    #download_url = "",
    license = "LGPL License",
    packages = ["indexator", "indexator.log"],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]
    )
