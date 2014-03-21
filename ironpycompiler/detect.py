#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for detecting where the IronPython executables exist.

"""

import itertools
import os
import glob

# Original modules
from . import exceptions

def detect_ipy(regkeys = ["SOFTWARE\\IronPython", 
    "SOFTWARE\\Wow6432Node\\IronPython"], executable = "ipy.exe"):
    """This function returns the list of the paths to the IronPython directories.
    
    This function searches in the Windows registry and PATH for 
    IronPython. If IronPython cannot be found in your system, 
    :exc:`ironpycompiler.exceptions.IronPythonDetectionError` will occur.
    
    :param list regkeys: (optional) The IronPython registry keys that 
                         should be looked for.
    :param str executable: (optional) The name of the IronPython 
                           executable.
    :rtype: list
    
    """
    
    ipydirpaths = set()
    
    # 可能ならば、IronPythonキーをレジストリから読み込む
    ipybasekey = None
    try:
        import _winreg
    except ImportError as e:
        pass
    else:
        for key in regkeys:
            try:
                ipybasekey = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE, key)
            except WindowsError as e: # キーが存在しないときなど
                continue
            else:
                break # キーが存在したら終わる
    
    # レジストリからIronPythonへのパスを取得する
    if ipybasekey:
        itr = itertools.count()
        # インストールされているIronPythonのバージョンを取得する
        ipyvers = []
        for idx in itr:
            try:
                ipyvers.append(
                _winreg.EnumKey(ipybasekey, idx))
            except WindowsError as e: # 対応するサブキーがなくなったら
                break
        # IronPythonへのパスを取得する
        for ver in ipyvers:
            with _winreg.OpenKey(ipybasekey, 
            ver + "\\InstallPath") as ipypathkey:
                ipydirpaths.add(os.path.dirname(
                _winreg.QueryValue(ipypathkey, None)))
        # IronPythonキーを閉じる
        ipybasekey.Close()
    
    # 環境変数PATHからIronPythonへのパスを取得する
    for path in os.environ["PATH"].split(os.pathsep):
        for match_path in glob.glob(os.path.join(path, executable)):
            if os.access(match_path, os.X_OK):
                ipydirpaths.add(os.path.dirname(match_path))
    
    if len(ipydirpaths) == 0:
        raise exceptions.IronPythonDetectionError(executable)
    
    return sorted(list(ipydirpaths), reverse = True)

