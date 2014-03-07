IronCompiler
============

IronCompiler will be useful for compiling your IronPython scripts 
requiring modules from the Python standard library (or third-party 
pure-Python modules) into .NET assembly, using pyc.py.

This module is supposed to be used on *CPython*, not IronPython, because 
``modulefinder`` of IronPython does not work correctly.

.. note:: This module is still unstable and its documents are incomplete.

Main Features
-------------

* Detect the path of the directory where the IronPython 
executables exist
* Check what modules your IronPython scripts require
* Compile your scripts into a stand-alone .NET assembly

Author
------

* Hamukichi (Nombiri)

