#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a command-line tool for IronPyCompiler.

Function defined in this module should not be used directly by other 
modules.
"""

import argparse
import os

# Original modules
import ironpycompiler
import ironpycompiler.compiler

# Third-party modules
import six

__version__ = ironpycompiler.__version__

def _compiler(args):
    """Funciton for command ``compile``. It should not be used directly.
    
    """
    mc = ironpycompiler.compiler.ModuleCompiler(
    paths_to_scripts = args.script)
    
    if args.target == "winexe" or args.target == "exe":
        if (args.main is not None) and (not args.main in args.script):
            args.script.insert(0, arg.main)
    
    if args.target == "winexe":
        mc.create_executable(out = args.out, winexe = True, 
        target_platform = args.platform, embed = args.embed, 
        standalone = args.standalone, mta = args.mta)
    elif args.target == "exe":
        mc.create_executable(out = args.out, winexe = False, 
        target_platform = args.platform, embed = args.embed, 
        standalone = args.standalone)
    else:
        mc.create_dll(out = args.out)
    
    six.print_(mc.pyc_stdout)

def main():
    """This function will be used when this module is run as a script.
        
    """
    # トップレベル
    parser = argparse.ArgumentParser(
    description = "Compile IronPython scripts into a .NET assembly.", 
    epilog = "See '%(prog)s <command> --help' for details.")
    parser.add_argument("-v", "--version", action = "version", 
    version = "IronPyCompiler " + __version__, 
    help = "Show the version of this module.")
    subparsers = parser.add_subparsers(
    help = "Commands this module accepts.", 
    dest = "command")
    
    # サブコマンドcompile
    parser_compile = subparsers.add_parser("compile", 
    help = "Analyze scripts and compile them.")
    parser_compile.add_argument("script", nargs = "+", 
    help = "Scripts that should be compiled.")
    parser_compile.add_argument("-o", "--out", 
    help = "Output file name.")
    parser_compile.add_argument("-t", "--target",
    default = "dll", choices = ["dll", "exe", "winexe"], 
    help = "Compile scripts into dll, exe, or winexe.")
    parser_compile.add_argument("-m", "--main",
    help = "Script to be executed first.")
    parser_compile.add_argument("-p", "--platform", 
    choices = ["x86", "x64"], 
    help = "Target platform.")
    parser_compile.add_argument("-e", "--embed", 
    action = "store_true", 
    help = "Embed the generated DLL into exe/winexe.")
    parser_compile.add_argument("-s", "--standalone", 
    action = "store_true", 
    help = "Embed the IronPython assemblies into exe/winexe.")
    parser_compile.add_argument("-M", "--mta", 
    action = "store_true", 
    help = "Set MTAThreadAttribute (winexe).")
    parser_compile.set_defaults(func = _compiler)
    
    args = parser.parse_args()
    
    # 将来Python 3.3+に対応したときに必要
    if hasattr(args, "func"):
        args.func(args)
    else:
         parser.print_help()

if __name__ == "__main__":
    main()
