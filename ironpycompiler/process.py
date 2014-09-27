#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module for communicating the IronPython process.

"""

import subprocess
import os


def execute_ipy(path_to_exe, arguments, cwd=None):
    """Executes the IronPython executable with the provided arguments.

    :param str path_to_exe: The path to the IronPython executable.
    :param list arguments: The arguments that should be passed to the
                           IronPython executable.
    :param str cwd: Specify the working directory, or :func:`os.getcwd` will
                    be used.
    :return: A tuple containing a string showing stdout/stderr, and the
             return code
    :rtype: tuple

    .. note::

       * The parameter ``args`` *should not* starts with the name of the
         IronPython executable. For example::

           path_to_exe = r"C:\IronPython27\ipy.exe"
           args = [path_to_exe, "-c", "print 'Hello!'"]  # Bad
           args = ["-c", "print 'Hello!'"]  # Good

       * Generally this function should not be used directly unless you intend
         to modify or extend IronPyCompiler.
    """

    ipy_sp = subprocess.Popen(
        args=[os.path.basename(path_to_exe)] + arguments,
        executable=path_to_exe, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, universal_newlines=True,
        cwd=(cwd if cwd is not None else os.getcwd()))
    output = ipy_sp.communicate()
    return (output[0], ipy_sp.returncode)
