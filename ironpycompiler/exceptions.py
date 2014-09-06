#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module contains execptions of IronPyCompiler.

"""


class IPCError(Exception):

    """This is the base class for exceptions in this module.

    """
    pass


class IronPythonDetectionError(IPCError):

    """This exception will be raised if IronPython cannot be found in your system.

    :param str executable: (optional) The name of the IronPython
                           executable looked for. This argument remains
                           for backward compatibility.
    :param msg: (optional) The detailed information of the error.

    .. versionchanged:: 0.9.0
       The argument ``executable`` became optional, and ``msg`` was added.

    """

    def __init__(self, executable=None, msg=None):
        self.executable = executable
        self.msg = msg

    def __str__(self):
        if self.executable is not None:
            return "IronPython (%s) cannot be found." % str(self.executable)
        elif self.msg is not None:
            return str(self.msg)
        else:
            return "IronPython cannot be found."


class ModuleCompilationError(IPCError):

    """This exception means an error during compilation.

    :param msg: (optional) The detailed information of the error.

    .. versionadded:: 0.10.0

    """

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        if self.msg is not None:
            return str(self.msg)
        else:
            return "An error occurred during compilation."
