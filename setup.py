#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script for installing IronPyCompiler.

"""

from __future__ import with_statement
from setuptools import setup
import sys

import ironpycompiler

# Read README.txt and HISTORY.txt
with open("README.txt", "r") as f_readme:
    readme_content = f_readme.read()
with open("HISTORY.txt", "r") as f_history:
    history_content = f_history.read() 

sysver = sys.version_info

classifiers = ["Development Status :: 4 - Beta", 
               "Intended Audience :: Developers", 
               "License :: OSI Approved :: MIT License", 
               "Operating System :: Microsoft :: Windows", 
               "Programming Language :: Python", 
               "Programming Language :: Python :: 2", 
               "Programming Language :: Python :: 2.7", 
               "Programming Language :: Python :: Implementation :: CPython", 
               "Topic :: Software Development", 
               "Topic :: System :: Software Distribution"]

setup_args = {"name": "ironpycompiler",
              "version": ironpycompiler.__version__,
              "description": "Compile IronPython scripts into a stand-alone .NET assembly.", 
              "long_description": readme_content + "\n\n" + history_content, 
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
