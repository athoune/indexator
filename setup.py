#!/usr/bin/env python

"""Setup script for the pyparsing module distribution."""
from setuptools import setup, find_packages

setup(# Distribution meta-data
    name = "indexator",
    version = '0.1',
    description = "Index",
    author = "Mathieu Lecarme",
    author_email = "mathieu@garambrogne.net",
    url = "http://github.com/athoune/indexator/tree/master",
    #download_url = "",
    license = "LGPL License",
    package_dir = {'': 'src'},
    packages = ["indexator", "indexator.log"],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Development Status :: 1 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",
        ],
    test_suite = "test",
    )
