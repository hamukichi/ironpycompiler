#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for detecting where the IronPython executables exist.

"""

import itertools
import os
import glob
import subprocess
import sys
import re

# Original modules
from . import exceptions
from . import constants
from . import datatypes


def search_ipy_reg(regkeys=None):
    """Search for IronPython regisitry keys.

    This function searches for IronPython keys in the Windows registry,
    and returns a dictionary showing the versions of IronPython and their
    locations (the paths to the IronPython directories).

    :param list regkeys: (optional) The IronPython registry keys that
                         should be looked for.
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
        raise exceptions.IronPythonDetectionError(
            msg="Could not find any IronPython registry key.")
    else:
        itr = itertools.count()
        for idx in itr:
            try:
                foundipys[_winreg.EnumKey(ipybasekey, idx)] = None
            except WindowsError:  # 対応するサブキーがなくなったら
                break
        if foundipys == dict():
            raise exceptions.IronPythonDetectionError(
                msg="Could not find any version of IronPython.")
        for ver in foundipys:
            ipypathkey = _winreg.OpenKey(ipybasekey,
                                         ver + "\\InstallPath")
            foundipys[ver] = os.path.dirname(
                _winreg.QueryValue(ipypathkey, None))
            ipypathkey.Close()
        ipybasekey.Close()

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
            ipy_ver = validate_ipyexe(ipy_exe)
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


def search_ipy(regkeys=None, executable=constants.EXECUTABLE):
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
        foundipys = search_ipy_reg(regkeys)
    except exceptions.IronPythonDetectionError:
        foundipys = dict()

    try:
        envipys = search_ipy_env(executable)
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
    :raises ironpycompiler.exceptions.IronPythonDetectionError: if this
                                                                function could
                                                                not decide the
                                                                optimum version

    .. versionadded:: 0.9.0

    """

    cpy_ver = sys.version_info
    cpy_ver_str = "%d.%d" % (cpy_ver[0], cpy_ver[1])
    foundipys = search_ipy()

    if cpy_ver_str in foundipys:
        return (cpy_ver_str, foundipys[cpy_ver_str])
    else:
        # メジャーバージョンは合致するがマイナーバージョンは合致しないバージョン
        majoripys = sorted(
            [ver for ver in foundipys.keys() if ver.startswith(
                "%d." % cpy_ver[0])],
            reverse=True)
        if len(majoripys) == 0:
            raise exceptions.IronPythonDetectionError(
                msg="Could not decide the optimum version of IronPython.")
        else:
            return (majoripys[0], foundipys[majoripys[0]])


def validate_ipyexe(path_to_exe):
    """Check if the specified executable is a valid IronPython one.

    This function validate the executable file by executing it actually, and
    returns its version number.

    :param str path_to_exe: The path to the executable.
    :return: The version number of IronPython.
    :rtype: :class:`ironpycompiler.datatypes.HashableVersion`

    .. versionadded:: 1.0.0
    """

    verpattern = re.compile(r"[0-9]+[.]{1}[0-9]+")

    ipy_sp = subprocess.Popen(
        args=[os.path.basename(path_to_exe), "-c",
              "from platform import python_version as pv; print pv()"],
        executable=path_to_exe, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True)

    (ipy_stdout, ipy_stderr) = ipy_sp.communicate()
    ipy_ver = ipy_stdout.strip()
    if re.match(verpattern, ipy_ver) is None:
        raise exceptions.IronPythonValidationError(
            "{} is not a valid IronPython executable.".format(path_to_exe))
    else:
        return datatypes.HashableVersion(ipy_ver)
