#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script for installing IronPyCompiler.

"""

from setuptools import setup
import sys

import ironpycompiler

# Read README.txt
with open("README.txt", "r") as f:
    readme_content = f.read()

sysver = sys.version_info

classifiers = ["Development Status :: 3 - Alpha", 
               "Intended Audience :: Developers", 
               "License :: OSI Approved :: MIT License", 
               "Operating System :: Microsoft :: Windows", 
               "Programming Language :: Python", 
               "Programming Language :: Python :: 2", 
               "Programming Language :: Python :: Implementation :: CPython", 
               "Programming Language :: Python :: Implementation :: PyPy", 
               "Topic :: Software Development", 
               "Topic :: System :: Software Distribution"]

setup_args = {"name": "ironpycompiler",
              "version": ironpycompiler.__version__,
              "description": "Compile IronPython scripts into a stand-alone .NET assembly.", 
              "long_description": readme_content, 
              "author": "Hamukichi (Nombiri)", 
              "author_email": "hamukichi-dev@outlook.jp",
              "packages": ["ironpycompiler"],
              "provides": ["ironpycompiler"],
              "url": "https://github.com/hamukichi/ironpycompiler", 
              "classifiers": classifiers, 
              "license" : "MIT License", 
              "keywords": ["ironpython", ".net", "assembly", "executable", 
                   "compile", "stand-alone", "pyc.py"], 
              "install_requires": [], 
              "entry_points": {"console_scripts": 
                        ["ipy2asm = ironpycompiler.ipy2asm:main"]}}

if sysver[0] == 2 and sysver[1] < 7:
    setup_args["install_requires"].append("argparse")

setup(**setup_args)
