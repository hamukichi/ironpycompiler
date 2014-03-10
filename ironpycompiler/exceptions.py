#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module contains execptions of IronPyCompiler.

"""

class IPCError(Exception):
    """This is the base class for exceptions in this module.
    
    """
    pass

class IronPythonDetectionError(IPCError):
    """This exception will be raised when IronPython cannot be found in your system.
    
    :param str executable: The name of the IronPython executable looked for.
    
    """
    
    def __init__(self, exectuable):
        self.executable = str(executable)
    
    def __str__(self):
        return "IronPython (%s) cannot be found." % self.executable


        
