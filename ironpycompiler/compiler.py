#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for analyzing and compiling IronPython scripts.

"""

import sys
import os
import modulefinder
import tempfile
import glob
import shutil

# Original modules
from . import detect
from . import constants
from . import exceptions
from . import process


class ModuleCompiler(object):

    """Finds the modules required by your script and create a .NET assembly.

    By default this class searches for pure-Python modules in the
    IronPython standard library and the CPython site-packages directory.

    :param list paths_to_scripts: Specify the paths to your scripts.
                                  In creating a .EXE file, the first
                                  element of this list must be the
                                  path to the main file of your project.
    :param str ipy_dir: Specify the IronPython directory, or it will be
                        automatically detected using
                        :func:`ironpycompiler.detect.auto_detect`.
    :param str pyc_path: (optional) Specify the path to pyc.py.

    .. versionchanged:: 0.10.0
       The argument ``pyc_path`` was added.

    """

    def __init__(self, paths_to_scripts, ipy_dir=None, pyc_path=None):
        """ Initialization.
        """

        if ipy_dir is None:
            self.ipy_dir = detect.auto_detect()[1]
        else:
            self.ipy_dir = ipy_dir
        if pyc_path is None:
            self.pyc_abspath = os.path.join(self.ipy_dir,
                                            "Tools", "Scripts", "pyc.py")
        else:
            self.pyc_abspath = os.path.abspath(pyc_path)

        self.paths_to_scripts = [os.path.abspath(x) for x in
                                 paths_to_scripts]  # コンパイルすべきスクリプトたち
        self.dirs_of_modules = None  # 依存モジュールたちのディレクトリ
        #: Set of the names of built-in modules.
        self.builtin_modules = set()
        #: Set of the paths to required and compilable modules.
        self.compilable_modules = set()
        #: Set of the names of required but uncompilable modules.
        self.uncompilable_modules = set()
        self.response_file = None  # pyc.pyに渡すレスポンスファイル
        #: Output from pyc.py (stdout and stderr).
        self.pyc_stdout = None
        self.pyc_stderr = None  # pyc.pyから得た標準エラー出力、不要
        #: The path to the main output assembly.
        self.output_asm = None

    def check_compilability(self, dirs_of_modules=None):
        """Check the compilability of the modules required by the scripts.

        This method analyzes the scripts with
        :class:`modulefinder.ModuleFinder`. To get the results, access
        :attr:`builtin_modules`, :attr:`compilable_modules`, and
        :attr:`uncompilable_modules`.

        :param list dirs_of_modules: Specify the paths of the
                                     directories where the modules your
                                     scripts require exist, or this
                                     method searches for pure-Python
                                     modules in the IronPython standard
                                     library, and the CPython site-packages
                                     directory.

        """

        self.dirs_of_modules = dirs_of_modules
        if self.dirs_of_modules is None:
            self.dirs_of_modules = [os.path.join(self.ipy_dir,
                                                 "Lib")]
            self.dirs_of_modules += [p for p in sys.path if
                                     "site-packages" in p]

        # 各スクリプトが依存するモジュールを探索する
        for script in self.paths_to_scripts:
            mf = modulefinder.ModuleFinder(path=self.dirs_of_modules)
            mf.run_script(script)
            self.uncompilable_modules |= set(mf.badmodules.keys())
            for name, module in mf.modules.iteritems():
                path_to_module = module.__file__
                if path_to_module is None:
                    self.builtin_modules.add(name)
                    continue
                elif os.path.splitext(path_to_module)[1] == ".pyd":
                    self.uncompilable_modules.add(name)
                    continue
                else:
                    self.compilable_modules.add(
                        os.path.abspath(path_to_module))
        self.compilable_modules -= set(self.paths_to_scripts)

    def call_pyc(self, args, delete_resp=True,
                 executable=constants.EXECUTABLE, cwd=None):
        """Call pyc.py in order to compile your scripts.

        In general use this method is not supposed to be called
        directly. It is recommended that you use
        :meth:`create_asm` instead.

        :param list args: Specify the arguments that should be sent to
                          pyc.py.
        :param bool delete_resp: (optional) Specify whether to delete the
                                 response file after compilation or not.
        :param str executable: (optional) Specify the name of the
                               Ironpython exectuable.
        :param str cwd: (optional) Specify the current working directory.

        .. versionchanged:: 1.0.0
           Now uses :func:`ironpycompiler.process.execute_ipy`.

        """

        if cwd is None:
            cwd = os.getcwd()

        # レスポンスファイルを作る
        self.response_file = tempfile.mkstemp(suffix=".txt",
                                              text=True, prefix="IPC")

        # レスポンスファイルに書き込む
        for line in args:
            os.write(self.response_file[0], line + "\n")

        # レスポンスファイルを閉じる
        os.close(self.response_file[0])

        # pyc.pyを実行する
        ipy_args = [self.pyc_abspath, "@" + self.response_file[1]]
        ipy_exe = os.path.abspath(os.path.join(self.ipy_dir, executable))
        ipy_result = process.execute_ipy(arguments=ipy_args,
                                         path_to_exe=ipy_exe, cwd=cwd)
        self.pyc_stdout = ipy_result[0]

        # レスポンスファイルを削除する
        if delete_resp:
            os.remove(self.response_file[1])

        # ipyのエラーを確認する
        if ipy_result[1] != 0:
            raise exceptions.ModuleCompilationError(
                msg="{0} returned {1} exit status.".format(executable,
                                                           ipy_result[1]))

    def create_asm(self, out=None, target_asm="dll", target_platform=None,
                   embed=True, standalone=True, mta=False, delete_resp=True,
                   executable=constants.EXECUTABLE, copy_ipydll=False):
        """Compile your scripts into a .NET assembly, using pyc.py.

        This method compiles the scripts by calling pyc.py. If
        :attr:`compilable_modules` is empty, the scripts will be
        analyzed using :meth:`check_compilability`. For the detail of
        compilation see the source code of pyc.py.

        :param str out: (optional) Specify the name of the EXE file
                        that should be created, or the name of the main
                        script will be used and the destination
                        directory will be the current directory.
        :param str target_asm: (optional) The type of the output assembly,
                               can be "dll", "exe", or "winexe".
                               By default a .DLL file will be created.
        :param str target_platform: (optional) Specify the target
                                    platform ("x86" or "x64") if
                                    necessary (exe/winexe).
        :param bool embed: (optional) Specify whether to embed the
                           generated DLL into the executable (exe/winexe).
        :param bool standalone: (optional) Specify whether to embed
                                IronPython assemblies into the executable
                                (exe/winexe).
        :param bool mta: (optional) Specify whether to set
                         MTAThreadAttribute (winexe).
        :param bool delete_resp: (optional) Specify whether to delete the
                                 response file after compilation or not.
        :param str executable: (optional) Specify the name of the
                               Ironpython exectuable.
        :param bool copy_ipydll: (optional) Specify whether to copy the
                                 IronPython DLL files into the
                                 destination directory.

        """

        if self.compilable_modules == set():
            self.check_compilability()

        if out is None:
            output_basename = os.path.splitext(os.path.basename(
                self.paths_to_scripts[0]))[0]
            if target_asm in ["exe", "winexe"]:
                output_basename += ".exe"
            else:
                output_basename += ".dll"
            self.output_asm = os.path.join(os.getcwd(), output_basename)
        else:
            self.output_asm = os.path.abspath(out)

        pyc_args = ["/out:" + os.path.splitext(self.output_asm)[0]]

        if target_asm in ["exe", "winexe"]:
            pyc_args.append("/target:" + target_asm)
            pyc_args.append("/main:" + self.paths_to_scripts[0])
            if target_platform in ["x86", "x64"]:
                pyc_args.append("/platform:" + target_platform)
            if embed:
                pyc_args.append("/embed")
            if standalone:
                pyc_args.append("/standalone")
        if target_asm == "winexe" and mta:
            pyc_args.append("/mta")
        pyc_args += self.paths_to_scripts
        pyc_args += self.compilable_modules

        call_args = {"args": pyc_args, "delete_resp": delete_resp,
                     "executable": executable,
                     "cwd": os.path.dirname(self.output_asm)}

        self.call_pyc(**call_args)

        if copy_ipydll:
            gather_ipydll(dest_dir=os.path.dirname(self.output_asm),
                          ipy_dir=self.ipy_dir)


def gather_ipydll(dest_dir, ipy_dir=None):
    """ Copy the IronPython DLL files into the directory specified.

    :param str dest_dir: The path of the destination directory.
    :param str ipy_dir: Specify the path of the IronPython directory, or
                        it will be detected using
                        :func:`ironpycompiler.detect.auto_detect`.

    .. versionadded:: 0.9.0

    .. versionchanged:: 0.10.0
       This function now uses :func:`ironpycompiler.detect.auto_detect`.

    """

    if ipy_dir is None:
        ipy_dir = detect.auto_detect()[1]
    for dll in glob.glob(os.path.join(ipy_dir, "*.dll")):
        shutil.copy2(dll, dest_dir)
