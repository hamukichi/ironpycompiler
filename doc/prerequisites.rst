Prerequisites
=============

Environment
-----------

IronPyCompiler requires both IronPython 2.x and CPython 2.x. It was  
tested on IronPython 2.7.4 and CPython 2.7.5.

.. note::
   IronPyCompiler must be run on **CPython**, although it use IronPython 
   and its ``pyc.py``. This is because :mod:`modulefinder` of IronPython
   does not work correctly.

External Modules
----------------

* `argparse <https://pypi.python.org/pypi/argparse/1.2.1>`_ is necessary
  if you use CPython < 2.7.
