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
    
    :param str executable: (optional) The name of the IronPython executable looked for.
    
    .. versionchanged:: 0.9.0
       The argument ``executable`` became optional.
    
    """
    
    def __init__(self, exectuable = None):
        if executable is None:
            self.executable = None
        else:
            self.executable = str(executable)
    
    def __str__(self):
        if self.executable is None:
            return "IronPython cannot be found."
        else:
            return "IronPython (%s) cannot be found." % self.executable


        
