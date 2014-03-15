IronPyCompiler
==============

IronPyCompiler is a library for compiling IronPython scripts 
requiring modules from the Python standard library (or third-party 
pure-Python modules) into a *stand-alone* .NET assembly (a DLL file
or an executable), using pyc.py.

In order to compile IronPython scripts, we can use ``pyc.py``, which is 
included in the IronPython distribution. However, ``pyc.py`` does not 
check dependecies of the scripts, which results in a incomplete .NET
assembly. What is worse, the module ``modulefinder`` of IronPython 
does not work correctly. This is why compiling IronPython scripts is 
more difficult than it looks.

IronPyCompiler will solve this problem. It examines what modules your
scripts require, using the module ``modulefinder`` of **CPython**, and 
compiles them with ``pyc.py`` into a stand-alone .NET assembly, calling 
ipy.exe.
