Development
===========

GUI
---

To convert the mainwindow.ui file to a python class, use the following command:

On Windows:

.. code-block:: bash

  pyuic5 surfaceS\ui\mainwindow.ui -o surfaceS\ui\mainwindow.py

On linux:

.. code-block:: bash

  pyuic5 surfaceS/ui/mainwindow.ui -o surfaceS/ui/mainwindow.py

Documentation
-------------

To generate the *html* documentation, use the following command:

On Windows:

.. code-block:: bash

  sphinx-build -b html doc\source doc\build

On linux:

.. code-block:: bash

  sphinx-build -b html doc/source doc/build

To generate the latex documentation, use the following command:

On linux:

.. code-block:: bash

  sphinx-build -a -b latex doc/source doc/build-latex
  cd ./doc/build-latex/
  make
