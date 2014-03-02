#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helps to compile IronPython scripts, using pyc.py.

This module helps you compile your IronPython scripts which requires the Python 
standard library (or third-party pure-Python modules) into .NET assembly, using 
pyc.py.
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.1.0"
__date__ = "2014-03-03"
__licence__ = "MIT License"

import sys
import itertools
import os
import glob
import modulefinder
import site

# Third-party modules
from six import print_

IPYREGKEYS = ["SOFTWARE\\IronPython", "SOFTWARE\\Wow6432Node\\IronPython"]
IPYEXE = "ipy.exe"
DLLNAME = "StdLib.dll"

class PCHError(Exception):
    """This is the base class for exceptions in this module.
    """
    pass

class IronPythonDetectionError(PCHError):
    """This exception will be raised when IronPython cannot be found 
    in your system.
    
    :param str executable: The name of the IronPython executable looked for.
    """
    
    def __init__(self, exectuable):
        self.executable = str(executable)
    
    def __str__(self):
        return "IronPython (%s) cannot be found in your system." % self.executable

def detect_ipy(regkeys = IPYREGKEYS, executable = IPYEXE):
    """This function returns the list of the paths to the IronPython directories.
    
    This function searches in the Windows registry and PATH for IronPython.
    If IronPython cannot be found in your system, ``IronPythonDetectionError`` will occur.
    
    :param list regkeys: (optional) The IronPython registry keys that should be looked for.
    :param str executable: (optional) The name of the IronPython executable.
    :rtype: list
    """
    
    ipydirpaths = set()
    
    # 可能ならば、IronPythonキーをレジストリから読み込む
    ipybasekey = None
    try:
        from six.moves import winreg
        for key in regkeys:
            try:
                ipybasekey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key)
                break # キーが見つかれば終わる
            except WindowsError as e: # キーが存在しないときなど
                continue
    except ImportError as e:
        pass
    
    # レジストリからIronPythonへのパスを取得する
    if ipybasekey:
        itr = itertools.count()
        # インストールされているIronPythonのバージョンを取得する
        ipyvers = []
        for idx in itr:
            try:
                ipyvers.append(winreg.EnumKey(ipybasekey, idx))
            except WindowsError as e: # インデックスに対応するサブキーがなくなったら
                break
        # IronPythonへのパスを取得する
        for ver in ipyvers:
            ipypathkey = winreg.OpenKey(ipybasekey, ver + "\\InstallPath")
            ipydirpaths.add(os.path.dirname(winreg.QueryValue(ipypathkey, None)))
            ipypathkey.Close()
        # IronPythonキーを閉じる
        ipybasekey.Close()
    
    # 環境変数PATHからIronPythonへのパスを取得する
    for path in os.environ["PATH"].split(os.pathsep):
        for match_path in glob.glob(os.path.join(path, executable)):
            if os.access(match_path, os.X_OK):
                ipydirpaths.add(os.path.dirname(match_path))
    
    if len(ipydirpaths) == 0:
        raise IronPythonDetectionError(executable)
    
    return sorted(list(ipydirpaths), reverse = True)

class ModuleCompiler(modulefinder.ModuleFinder):
    """This class finds the modules required by your script and 
    compiles them into a DLL file.
    
    By default this class searches for pure-Python modules in the IronPython 
    standard library and the CPython site-packages directory.
    
    The initialization method of this class accepts the following parameters 
    which that of modulefinder.Modulefinder class does. 
    
    :param list path:
    :param int debug:
    :param list excludes:
    :param list replace_paths:
    
    Additionally, it accepts the following parameter.
    
    :param str ipy_dir: Specify the IronPython directory, or ``detect_ipy()[0]`` will be used.
    """
    
    def __init__(self, path = None, debug = 0, excludes = [], replace_paths = [], 
                 ipy_dir = None):
        """ Initialization.
        """
        
        if ipy_dir is None:
            self.ipy_dir = detect_ipy()[0]
        else:
            self.ipy_dir = ipy_dir
        
        if path is None:
            path = [os.path.join(self.ipy_dir, "Lib")]
            path += [p for p in sys.path if "site-packages" in p]
        modulefinder.ModuleFinder.__init__(self, path, debug, excludes, replace_paths)
    
    def check_compilability(self, path_to_script):
        """Check the compilability of the modules required by the script you specify.
        
        :param str path_to_script: Specify the path to your script.
        """
        
        self.path_to_script = os.path.abspath(path_to_script)
        modulefinder.ModuleFinder.run_script(self, pathname = self.path_to_script)
        self.compilable_modules = [] # モジュール名とファイルパスのタプルのリスト
        self.uncompilable_modules = self.badmodules.keys() # モジュール名のリスト
        
        for name, module in self.modules.iteritems():
            path_to_module = module.__file__
            if path_to_module is None: # sysなどの内蔵モジュール
                continue
            if os.path.splitext(path_to_module)[1] == ".pyd":
                self.uncompilable_modules.append(name)
                continue
            self.compilable_modules.append((name, os.path.abspath(path_to_module)))

if __name__ == "__main__":
    pass

