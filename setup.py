#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script for installing IronPyCompiler.

"""

from distutils.core import setup

import ironpycompiler

setup(name = "ironpycompiler",
      version = ironpycompiler.__version__,
      description = "Compile IronPython scripts into a stand-alone .NET assembly", 
      author = "Hamukichi (Nombiri)", 
      author_email = "hamukichi-dev@outlook.jp",
      packages = ["ironpycompiler"]
      )
