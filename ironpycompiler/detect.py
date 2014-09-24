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
from . import datatypes
from . import process


def search_ipy_reg(regkeys=None, executable=constants.EXECUTABLE,
                   detailed=False):
    """Search for IronPython regisitry keys.

    This function searches for IronPython keys in the Windows registry,
    and returns a dictionary showing the versions of IronPython and their
    locations (the paths to the IronPython directories).

    :param list regkeys: (optional) The IronPython registry keys that
                         should be looked for.
    :param str executable: (optional) The name of the IronPython
                           executable.
    :param bool detailed: (optional) If this parameter is true, the key of the
                          dictionary will be an instance of
                          :class:`ironpycompiler.datatypes.HashableVersion`
                          instead of string, in order to provide detailed
                          information of versions.
    :rtype: dict
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if IronPython
                                                                keys cannot be
                                                                found

    .. versionadded:: 0.9.0

    .. versionchanged:: 0.10.1
       Solved the problem that the default value for the argument ``regkeys``
       was mutable.

    """

    if regkeys is None:
        regkeys = constants.REGKEYS

    try:
        import _winreg
    except ImportError:
        raise exceptions.IronPythonDetectionError(
            msg="Cannot import a module for accessing the Windows registry.")

    foundipys = dict()
    ipybasekey = None

    # IronPythonキーを読み込む
    for key in regkeys:
        try:
            ipybasekey = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE, key)
        except WindowsError:
            continue
        else:
            break

    if ipybasekey is None:
        ipybasekey.Close()
        raise exceptions.IronPythonDetectionError(
            msg="Could not find any IronPython registry key.")
    else:
        itr = itertools.count()
        foundvers = []
        for idx in itr:
            try:
                foundvers.append(_winreg.EnumKey(ipybasekey, idx))
            except WindowsError:  # 対応するサブキーがなくなったら
                break
        foundipys = dict()
        for ver in foundvers:
            ipypathkey = _winreg.OpenKey(ipybasekey,
                                         ver + "\\InstallPath")
            ipy_dir = os.path.dirname(_winreg.QueryValue(ipypathkey, None))
            ipy_exe = os.path.abspath(os.path.join(ipy_dir, executable))
            try:
                ipy_ver = validate_pythonexe(ipy_exe)
            except exceptions.IronPythonValidationError:
                continue
            else:
                if detailed:
                    foundipys[ipy_ver] = ipy_dir
                else:
                    foundipys[ipy_ver.major_minor()] = ipy_dir
            finally:
                ipypathkey.Close()
        ipybasekey.Close()

    if len(foundipys) == 0:
        raise exceptions.IronPythonDetectionError(
            msg="Could not find any IronPython executable.")

    return foundipys


def search_ipy_env(executable=constants.EXECUTABLE, detailed=False):
    """Search for IronPython directories included in the PATH variable.

    This function searches for IronPython executables in your system,
    reading the PATH environment variable, and gets their version
    numbers, executing the executables.

    This function returns a dictionary showing the versions of
    IronPython and their locations (the paths to the IronPython
    directories).

    :param str executable: (optional) The name of the IronPython
                           executable.
    :param bool detailed: (optional) If this parameter is true, the key of the
                          dictionary will be an instance of
                          :class:`ironpycompiler.datatypes.HashableVersion`
                          instead of string, in order to provide detailed
                          information of versions.
    :rtype: dict
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if IronPython
                                                                cannot be found

    .. versionadded:: 0.9.0

    .. versionchanged:: 1.0.0
       * New parameter ``detailed`` was added.
       * Improved validation of executables.

    """

    ipydirpaths = []
    foundipys = {}

    for path in os.environ["PATH"].split(os.pathsep):
        for match_path in glob.glob(os.path.join(path, executable)):
            if os.access(match_path, os.X_OK):
                ipydirpaths.append(os.path.dirname(match_path))

    if len(ipydirpaths) == 0:
        raise exceptions.IronPythonDetectionError(
            msg="Could not find any executable file named %s." % executable)

    for directory in ipydirpaths:
        ipy_exe = os.path.abspath(os.path.join(directory, executable))
        try:
            ipy_ver = validate_pythonexe(ipy_exe)
        except exceptions.IronPythonValidationError:
            continue
        else:
            if detailed:
                foundipys[ipy_ver] = directory
            else:
                foundipys[ipy_ver.major_minor()] = directory

    if len(foundipys) == 0:
        raise exceptions.IronPythonDetectionError(
            msg=("{} exists but is not the IronPython executable."
                 ).format(executable))
    else:
        return foundipys


def search_ipy(regkeys=None, executable=constants.EXECUTABLE, detailed=False):
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

    .. versionchanged:: 0.10.1
       Solved the problem that the default value for the argument ``regkeys``
       was mutable.

    """

    if regkeys is None:
        regkeys = constants.REGKEYS

    try:
        foundipys = search_ipy_reg(regkeys, executable, detailed)
    except exceptions.IronPythonDetectionError:
        foundipys = dict()

    try:
        envipys = search_ipy_env(executable, detailed)
    except exceptions.IronPythonDetectionError:
        envipys = dict()

    for k, v in envipys.items():
        if k not in foundipys:
            foundipys[k] = v

    if len(foundipys) == 0:
        raise exceptions.IronPythonDetectionError(
            msg="Could not find any IronPython directory.")
    else:
        return foundipys


def auto_detect(detailed=False):
    """Decide the optimum version of IronPython in your system.

    This function decides the most suitable version of IronPython
    in your system for the version of CPython on which IronPyCompiler
    is being run, and returns a tuple showing its version number and
    its location (the path to the IronPython directory).

    Example: On CPython 2.7, first this function searches for
    IronPython 2.7. If this fails, then the newest IronPython 2.x in
    your system will be selected.

    :rtype: tuple
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if this
                                                                function could
                                                                not decide the
                                                                optimum version

    .. versionadded:: 0.9.0

    """

    # The version of CPython
    cpy_ver = datatypes.HashableVersion()

    # The versions of IronPython
    foundipys = search_ipy(detailed=True)
    ipy_vers = foundipys.keys()

    # マイナー・メジャーバージョンが一致
    ipy_vers_minor = sorted([v for v in ipy_vers
                            if (cpy_ver.major == v.major)
                            and (cpy_ver.minor == v.minor)], reverse=True)

    # メジャーバージョンのみが一致
    ipy_vers_major = sorted([v for v in ipy_vers if cpy_ver.major == v.major],
                            reverse=True)

    if cpy_ver in ipy_vers:  # The same version number
        optimum_ipy_ver = cpy_ver
    elif ipy_vers_minor != []:
        optimum_ipy_ver = ipy_vers_minor[0]
    elif ipy_vers_major != []:
        optimum_ipy_ver = ipy_vers_major[0]
    else:
        raise exceptions.IronPythonDetectionError(
            "Could not find the optimum version of IronPython.")

    if detailed:
        return (optimum_ipy_ver, foundipys[optimum_ipy_ver])
    else:
        return (optimum_ipy_ver.major_minor(), foundipys[optimum_ipy_ver])


def validate_pythonexe(path_to_exe):
    """Check if the specified executable is a valid Python one.

    This function validate the executable file by executing it actually, and
    returns its version number.

    :param str path_to_exe: The path to the executable.
    :return: The version number of Python.
    :rtype: :class:`ironpycompiler.datatypes.HashableVersion`

    .. versionadded:: 1.0.0
    """

    try:
        (ipy_stdout, ipy_stderr) = process.execute_ipy(
            arguments=["-c",
                       "from platform import python_version as pv; print pv()"],
            path_to_exe=path_to_exe)
    except EnvironmentError as e:
        raise exceptions.IronPythonValidationError(
            "{} is not available: {}".format(path_to_exe, str(e)))
    else:
        ipy_ver_str = ipy_stdout.strip()
        try:
            ipy_ver = datatypes.HashableVersion(ipy_ver_str)
        except ValueError:
            raise exceptions.IronPythonValidationError(
                "{} is not a valid IronPython executable:".format(path_to_exe))
        else:
            return ipy_ver
