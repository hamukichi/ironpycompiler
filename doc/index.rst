.. IronPyCompiler documentation master file, created by
   sphinx-quickstart on Sat Mar 15 22:44:27 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IronPyCompiler's documentation!
==========================================

IronPyCompiler is a library for compiling IronPython scripts 
requiring modules from the Python standard library (or third-party 
pure-Python modules) into a *stand-alone* .NET assembly (a DLL file
or an executable), using pyc.py.

In order to compile IronPython scripts, we can use ``pyc.py``, which is 
included in the IronPython distribution. However, ``pyc.py`` does not 
check dependecies of the scripts, which results in an incomplete .NET
assembly. What is worse, the module ``modulefinder`` of IronPython 
does not work correctly. This is why compiling IronPython scripts is 
more difficult than it looks.

IronPyCompiler will solve this problem. It examines what modules your
scripts require, using the module ``modulefinder`` of **CPython**, and 
compiles them with ``pyc.py`` into a stand-alone .NET assembly, calling 
ipy.exe.

.. toctree::
   :maxdepth: 2
   
   prerequisites
   installation
   command-line
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

