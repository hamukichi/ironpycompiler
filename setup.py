#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script for installing IronPyCompiler.

"""


from setuptools import setup

import ironpycompiler

# Read README.txt
with open("README.txt", "r") as f:
    readme_content = f.read()

setup(name = "ironpycompiler",
      version = ironpycompiler.__version__,
      description = "Compile IronPython scripts into a stand-alone .NET assembly.", 
      long_description = readme_content, 
      author = "Hamukichi (Nombiri)", 
      author_email = "hamukichi-dev@outlook.jp",
      packages = ["ironpycompiler"], 
      install_requires = ["argparse"], 
      provides = ["ironpycompiler"], 
      scripts = ["ipy2asm.py"], 
      url = "https://github.com/hamukichi/ironpycompiler", 
      classifiers = ["Development Status :: 3 - Alpha", 
                     "Intended Audience :: Developers", 
                     "License :: OSI Approved :: MIT License", 
                     "Operating System :: Microsoft :: Windows", 
                     "Programming Language :: Python", 
                     "Programming Language :: Python :: 2", 
                     "Programming Language :: Python :: Implementation :: CPython", 
                     "Programming Language :: Python :: Implementation :: PyPy", 
                     "Topic :: Software Development", 
                     "Topic :: System :: Software Distribution"],
      license = "MIT License", 
      keywords = ["ironpython", ".net", "assembly", "executable", "compile", "stand-alone", "pyc.py"], 
      entry_points = {"console_scripts": ["ipy2asm = ironpycompiler.ip2asm:main"]}
      )
