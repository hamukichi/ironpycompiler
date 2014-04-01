Prerequisites
=============

Environment
-----------

IronPyCompiler requires both IronPython 2.x and CPython 2.x. It was  
tested on IronPython 2.7.4 and CPython 2.7.5.

.. note::
   * IronPyCompiler must be run on **CPython**, although it use IronPython 
     and its ``pyc.py``. This is because :mod:`modulefinder` of IronPython
     does not work correctly, while that of CPython does.
   * IronPyCompiler will not work on CPython 3.x, which is not compatible
     with the latest stable version of IronPython.

External Modules
----------------

* `argparse <https://pypi.python.org/pypi/argparse/1.2.1>`_ is necessary
  if you use CPython < 2.7.
* `setuptools <https://pypi.python.org/pypi/setuptools>`_ is required in
  installing IronPyCompiler using ``setup.py``.
