#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for detecting where the IronPython executables exist.

"""

import itertools
import os
import glob
import subprocess
import warnings
import sys

# Original modules
from . import exceptions
from . import constants

def detect_ipy(regkeys = constants.REGKEYS, executable = constants.EXECUTABLE):
    """This function returns the list of the paths to the IronPython directories.
    
    This function searches in the Windows registry and PATH for 
    IronPython.
    
    :param list regkeys: (optional) The IronPython registry keys that 
                         should be looked for.
    :param str executable: (optional) The name of the IronPython 
                           executable.
    :rtype: list
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if IronPython cannot be found
    
    .. versionchanged:: 0.9.0
       This function now calls :func:`search_ipy`.
    
    .. warning::
       This function is deprecated, and will be removed in the next 
       major version. Please use :func:`search_ipy`.
    
    """
    
    warnings.warn("Use search_ipy instead.", DeprecationWarning)

    return sorted(search_ipy(regkeys, executable).values(), reverse = True)

def search_ipy_reg(regkeys = None):
    """Search for IronPython regisitry keys.
    
    This function searches for IronPython keys in the Windows registry, 
    and returns a dictionary showing the versions of IronPython and their
    locations (the paths to the IronPython directories).
    
    :param list regkeys: (optional) The IronPython registry keys that 
                         should be looked for.
    :rtype: dict
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if IronPython keys cannot be found
    
    .. versionadded:: 0.10.1
       Solved the problem that the default value for the argument ``regkeys`` was mutable.
    
    """
    
    if regkeys is None:
        regkeys = constants.REGKEYS
    
    try:
        import _winreg
    except ImportError as e:
        raise exceptions.IronPythonDetectionError(
        msg = "Unable to import a module for accessing the Windows registry.")
    
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
        raise exceptions.IronPythonDetectionError(
        msg = "Could not find any IronPython registry key.")
    else:
        itr = itertools.count()
        for idx in itr:
            try:
                foundipys[_winreg.EnumKey(ipybasekey, idx)] = None
            except WindowsError as e: # 対応するサブキーがなくなったら
                break
        if foundipys == dict():
            raise exceptions.IronPythonDetectionError(
            msg = "Could not find any version of IronPython.")
        for ver in foundipys:
            ipypathkey = _winreg.OpenKey(ipybasekey, 
            ver + "\\InstallPath")
            foundipys[ver] = os.path.dirname(
            _winreg.QueryValue(ipypathkey, None))
            ipypathkey.Close()
        ipybasekey.Close()
    
    return foundipys

def search_ipy_env(executable = constants.EXECUTABLE):
    """Search for IronPython directories included in the PATH variable.
    
    This function searches for IronPython executables in your system, 
    reading the PATH environment variable, and gets their version 
    numbers, executing the executables.
    
    This function returns a dictionary showing the versions of 
    IronPython and their locations (the paths to the IronPython 
    directories).
    
    :param str executable: (optional) The name of the IronPython 
                           executable.
    :rtype: dict
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if IronPython cannot be found
    
    .. versionadded:: 0.9.0
    
    """
    
    ipydirpaths = []
    foundipys = {}
    
    for path in os.environ["PATH"].split(os.pathsep):
        for match_path in glob.glob(os.path.join(path, executable)):
            if os.access(match_path, os.X_OK):
                ipydirpaths.append(os.path.dirname(match_path))
    
    if len(ipydirpaths) == 0:
        raise exceptions.IronPythonDetectionError(
        msg = "Could not find any executable file named %s." % executable)
    
    for directory in ipydirpaths:
        ipy_exe = os.path.abspath(os.path.join(directory, executable))
        sp = subprocess.Popen(
        args = [executable, "-V"], 
        executable = ipy_exe, stdin = subprocess.PIPE,
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        (sp_stdout, sp_stderr) = sp.communicate()
        ipy_ver = sp_stdout[11:14] #Todo: 正規表現でx.xのみを抽出
        foundipys[ipy_ver] = directory
    
    return foundipys

def search_ipy(regkeys = None, executable = constants.EXECUTABLE):
    """Search for IronPython directories.
    
    This function searches for IronPython directories using both
    :func:`search_ipy_env` and :func:`search_ipy_reg`, and returns a 
    dictionary showing the versions of IronPython and their locations 
    (the paths to the IronPython directories).
    
    :param str executable: (optional) The name of the IronPython 
                           executable.
    :param list regkeys: (optional) The IronPython registry keys that 
                         should be looked for.
    :rtype: dict
    
    .. versionadded:: 0.9.0
    
    .. versionadded:: 0.10.1
       Solved the problem that the default value for the argument ``regkeys`` was mutable.
    
    """ 
    
    if regkeys is None:
        regkeys = constants.REGKEYS
    
    try:
        foundipys = search_ipy_reg(regkeys)
    except exceptions.IronPythonDetectionError as e:
        foundipys = dict()
    
    try:
        envipys = search_ipy_env(executable)
    except exceptions.IronPythonDetectionError as e:
        envipys = dict()
    
    for k, v in envipys.items():
        if k not in foundipys:
            foundipys[k] = v
    
    if len(foundipys) == 0:
        raise exceptions.IronPythonDetectionError(
        msg = "Could not find any IronPython directory.")
    else:
        return foundipys

def auto_detect():
    """Decide the optimum version of IronPython in your system.
    
    This function decides the most suitable version of IronPython 
    in your system for the version of CPython on which IronPyCompiler
    is being run, and returns a tuple showing its version number and 
    its location (the path to the IronPython directory).
    
    Example: On CPython 2.7, first this function searches for
    IronPython 2.7. If this fails, then the newest IronPython 2.x in 
    your system will be selected.
    
    :rtype: tuple
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if this function could
                                                                not decide the optimum
                                                                version
    
    .. versionadded:: 0.9.0
    
    """
    
    cpy_ver = sys.version_info
    cpy_ver_str = "%d.%d" % (cpy_ver[0], cpy_ver[1])
    foundipys = search_ipy()
    
    if cpy_ver_str in foundipys:
        return (cpy_ver_str, foundipys[cpy_ver_str])
    else:
        #メジャーバージョンは合致するがマイナーバージョンは合致しないバージョンたち
        majoripys = sorted(
        [ver for ver in foundipys.keys() if ver.startswith("%d." % cpy_ver[0])], 
        reverse = True)
        if len(majoripys) == 0:
            raise exceptions.IronPythonDetectionError(
            msg = "Could not decide the optimum version of IronPython.")
        else:
            return (majoripys[0], foundipys[majoripys[0]])

    
