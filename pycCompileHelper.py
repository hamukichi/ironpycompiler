#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helps to compile IronPython scripts, using pyc.py.

This module helps you compile your IronPython scripts requiring the 
Python standard library (or third-party pure-Python modules) into a 
.NET assembly, using pyc.py.
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.3.0"
__date__ = "2014-03-06"
__licence__ = "MIT License"

import sys
import itertools
import os
import glob
import modulefinder
import tempfile

# Third-party modules
import six

IPYREGKEYS = ["SOFTWARE\\IronPython", 
"SOFTWARE\\Wow6432Node\\IronPython"]
IPYEXE = "ipy.exe"
DLLNAME = "StdLib.dll"

class PCHError(Exception):
    """This is the base class for exceptions in this module.
    """
    pass

class IronPythonDetectionError(PCHError):
    """This exception will be raised when IronPython cannot be found in 
    your system.
    
    :param str executable: The name of the IronPython executable looked 
    for.
    """
    
    def __init__(self, exectuable):
        self.executable = str(executable)
    
    def __str__(self):
        return "IronPython (%s) cannot be found." % self.executable

def detect_ipy(regkeys = IPYREGKEYS, executable = IPYEXE):
    """This function returns the list of the paths to the IronPython 
    directories.
    
    This function searches in the Windows registry and PATH for 
    IronPython. If IronPython cannot be found in your system, 
    ``IronPythonDetectionError`` will occur.
    
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
        for key in regkeys:
            try:
                ipybasekey = six.moves.winreg.OpenKey(
                six.moves.winreg.HKEY_LOCAL_MACHINE, key)
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
                ipyvers.append(
                six.moves.winreg.EnumKey(ipybasekey, idx))
            except WindowsError as e: # 対応するサブキーがなくなったら
                break
        # IronPythonへのパスを取得する
        for ver in ipyvers:
            with six.moves.winreg.OpenKey(ipybasekey, 
            ver + "\\InstallPath") as ipypathkey:
                ipydirpaths.add(os.path.dirname(
                six.moves.winreg.QueryValue(ipypathkey, None)))
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

class ModuleCompiler:
    """This class finds the modules required by your script and 
    create a .NET assembly.
    
    By default this class searches for pure-Python modules in the 
    IronPython standard library and the CPython site-packages directory.
    
    :param str ipy_dir: Specify the IronPython directory, or 
    ``detect_ipy()[0]`` will be used.
    :param list paths_to_scripts: Specify the paths to your scripts. 
    In creating a .EXE file, ``paths_to_scripts[0]`` must be the path 
    to the main file of your project.
    """
    
    def __init__(self, ipy_dir = None, paths_to_scripts):
        """ Initialization.
        """
        
        if ipy_dir is None:
            self.ipy_dir = detect_ipy()[0]
        else:
            self.ipy_dir = ipy_dir
        
        self.paths_to_scripts = [os.path.abspath(x) for x in 
        paths_to_scripts] # コンパイルすべきスクリプトたち
        
        self.dirs_of_modules = None # 依存モジュールたちのディレクトリ
        self.compilable_modules = set() # ファイルパスの集合
        self.uncompilable_modules = set() # モジュール名の集合、非必須
        self.response_file = None # pyc.pyに渡すレスポンスファイル
        
           
    def check_compilability(self, dirs_of_modules = None):
        """Check the compilability of the modules required by the 
        scripts you specified.
        
        :param list dirs_of_modules: Specify the paths of the 
        directories where the modules your scripts require exist, or 
        this method searches for pure-Python modules in the IronPython 
        standard library and the CPython site-packages directory.
        """
        
        self.dirs_of_modules = dirs_of_modules
        if self.dirs_of_modules is None:
                self.dirs_of_modules = [os.path.join(self.ipy_dir, 
                "Lib")]
                self.dirs_of_modules += [p for p in sys.path if 
                "site-packages" in p]
        
        # 各スクリプトが依存するモジュールを探索する
        for script in self.paths_to_scripts:
            mf = modulefinder.ModuleFinder(path = self.dirs_of_modules)
            mf.run_script(script)
            self.uncompilable_modules |= set(mf.badmodules.keys())
            for name, module in mf.modules.iteritems():
                path_to_module = module.__file__
                if path_to_module is None:
                    continue
                elif os.path.splitext(path_to_module)[1] == ".pyd":
                    self.uncompilable_modules.add(name)
                    continue
                else:
                    self.compilable_modules.add(
                    os.path.abspath(path_to_module))
        self.compilable_modules -= set(self.paths_to_scripts)
    
    def call_pyc(self, args, delete_resp = True):
        """Call pyc.py in order to compile your scripts.
        
        In general use this method is not supposed to be called 
        directly. It is recommended that you use ``create_exe`` or 
        ``create_dll`` instead.
        
        :param list args: Specify the arguments that should be sent to 
        pyc.py.
        :param bool delete_resp: Specify whether to delete the 
        response file after compilation.
        """
        
        # レスポンスファイルを作る
        self.response_file = tempfile.mkstemp(suffix = ".txt", 
        text = True)
        
        # レスポンスファイルに書き込む
        for line in args:
            os.write(self.response_file[0], line + "\n")
        
        # レスポンスファイルを閉じ、必要ならば削除する
        os.close(self.response_file[0])
        if delete_resp:
            os.remove(self.response_file[1])

        
if __name__ == "__main__":
    pass

