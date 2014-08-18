Command-line Tool
=================

IronPyCompiler has a command-line script named ``ipy2asm`` for convenience. This script
will be installed in the directory ``Scripts``.

Examples
--------

Compiling Scripts
^^^^^^^^^^^^^^^^^

Creating a .exe File and Copying IronPython DLLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none
   
   ipy2asm compile -o consoleapp.exe -t exe -m main1.py -e -s -c main1.py sub1.py
   ipy2asm compile -o winapp.exe -t winexe -m main2.py -e -s -M -c main2.py sub2.py

Creating a .dll File
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none
   
   ipy2asm compile -o libfoo.dll -t dll bar.py baz.py


Checking Modules Required by Scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: none
   
   ipy2asm analyze foo.py bar.py baz.py

Detailed Information
--------------------

Please see ``ipy2asm --help``.
