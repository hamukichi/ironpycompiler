#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Defines the data types used in IronPyCompiler.

"""

import distutils.version

class PythonVersion(distutils.version.StrictVersion):

    """Represents a Python version.

    """

    def __init__(self, vstring=None):
        distutils.version.StrictVersion.__init__(self)
        self.major = self.version[0]
        self.minor = self.version[1]
        self.patch = self.version[2]

