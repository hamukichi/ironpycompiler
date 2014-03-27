Command-line Tool
=================

IronPyCompiler has a command-line script named ``ipy2asm``. This script
will be installed in the directory ``Scripts``.

Examples
--------

Compiling Scripts into a .exe File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bat
   
   ipy2asm -o consoleapp.exe -t exe -m main1.py -e -s main1.py sub1.py
   ipy2asm -o winapp.exe -t winexe -m main2.py -e -s -M main2.py sub2.py

Compiling Scripts into a .dll File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bat
   
   ipy2asm -o libfoo.dll -t dll bar.py baz.py

Detailed Information
--------------------

Please see ``ipy2asm --help``.
