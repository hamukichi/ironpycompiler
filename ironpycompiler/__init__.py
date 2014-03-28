#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helps to compile IronPython scripts, using pyc.py.

This library helps you compile your IronPython scripts requiring the 
Python standard library (or third-party pure-Python modules) into a 
.NET assembly, using pyc.py.

.. note :: This library should be used on **CPython**, not IronPython, 
           because :mod:`modulefinder` of IronPython does not work 
           correctly.
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.9.0.a3"
__date__ = "2014-03-28"
__licence__ = "MIT License"

