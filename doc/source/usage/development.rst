Development
===========

GUI
---

To convert the mainwindow.ui file to a python class, use the following command
(windows):

.. code-block:: bash

  pyuic5 surfaceS\ui\mainwindow.ui -o surfaceS\ui\mainwindow.py

Documentation
-------------

To generate the documentation, the following command should be used:

.. code-block:: bash

  sphinx-build -b html doc\source doc\build
