#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for detecting where the IronPython executables exist.

"""

import itertools
import os
import glob
import subprocess

# Original modules
from . import exceptions
from . import constants

def detect_ipy(regkeys = constants.REGKEYS, executable = constants.EXECUTABLE):
    """This function returns the list of the paths to the IronPython directories.
    
    This function searches in the Windows registry and PATH for 
    IronPython. If IronPython cannot be found in your system, 
    :exc:`ironpycompiler.exceptions.IronPythonDetectionError` will occur.
    
    :param list regkeys: (optional) The IronPython registry keys that 
                         should be looked for.
    :param str executable: (optional) The name of the IronPython 
                           executable.
    :rtype: list
    
    .. versionchanged:: 0.9.0
       This function now calls :func:`search_ipy_reg` and
       :func:`search_ipy_env`.
    
    """
    
    ipydirpaths = set()
    
    try:
        for directory in search_ipy_reg(regkeys).itervalues():
            ipydirpaths.add(directory)
    except exceptions.IronPythonDetectionError():
        pass
    
    try:
        for directory in search_ipy_env(executable).itervalues():
            ipydirpaths.add(directory)
    except exceptions.IronPythonDetectionError():
        pass
    
    if len(ipydirpaths) == 0:
        raise exceptions.IronPythonDetectionError()
    else:
        return sorted(list(ipydirpaths), reverse = True)

def search_ipy_reg(regkeys = constants.REGKEYS):
    """
    Searches for IronPython regisitry keys.
    
    This function searches for IronPython keys in the Windows registry, 
    and returns a dictionary showing the versions of IronPython and their
    locations (the paths to the IronPython directories). If there is no
    IronPython registry key, 
    :exc:`ironpycompiler.exceptions.IronPythonDetectionError` will occur.
    
    :param list regkeys: (optional) The IronPython registry keys that 
                         should be looked for.
    :rtype: dict
    
    .. versionadded:: 0.9.0
    
    """
    
    import _winreg
    
    foundipys = dict()
    ipybasekey = None
    
    # IronPythonキーを読み込む
    for key in regkeys:
        try:
            ipybasekey = _winreg.OpenKey(
            _winreg.HKEY_LOCAL_MACHINE, key)
        except WindowsError as e:
            continue
        else:
            break
    
    if ipybasekey is None:
        raise exceptions.IronPythonDetectionError()
    else:
        itr = itertools.count()
        for idx in itr:
            try:
                foundipys[_winreg.EnumKey(ipybasekey, idx)] = None
            except WindowsError as e: # 対応するサブキーがなくなったら
                break
        for ver in foundipys:
            ipypathkey = _winreg.OpenKey(ipybasekey, 
            ver + "\\InstallPath")
            foundipys[ver] = os.path.dirname(
            _winreg.QueryValue(ipypathkey, None))
            ipypathkey.Close()
        ipybasekey.Close()
    
    return foundipys

def search_ipy_env(executable = constants.EXECUTABLE):
    """
    Searches for IronPython directories, reading the PATH variable.
    
    This function searches for IronPython executables in your system, 
    reading the PATH environment variable, and gets their version 
    numbers, executing the executables.
    
    This function returns a dictionary showing the versions of 
    IronPython and their locations (the paths to the IronPython 
    directories). If no IronPython executable is found, 
    :exc:`ironpycompiler.exceptions.IronPythonDetectionError` will occur.
    
    :param str executable: (optional) The name of the IronPython 
                           executable.
    :rtype: dict
    
    .. versionadded:: 0.9.0
    
    """
    
    ipydirpaths = []
    foundipys = {}
    
    for path in os.environ["PATH"].split(os.pathsep):
        for match_path in glob.glob(os.path.join(path, executable)):
            if os.access(match_path, os.X_OK):
                ipydirpaths.append(os.path.dirname(match_path))
    
    if len(ipydirpaths) == 0:
        raise IronPythonDetectionError(executable)
    
    for directory in ipydirpaths:
        ipy_exe = os.path.abspath(os.path.join(directory, executable))
        sp = subprocess.Popen(
        args = [executable, "-V"], 
        executable = ipy_exe, stdin = subprocess.PIPE,
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        (sp_stdout, sp_stderr) = sp.communicate()
        ipy_ver = sp_stdout[11:14]
        foundipys[ipy_ver] = directory
    
    return foundipys

