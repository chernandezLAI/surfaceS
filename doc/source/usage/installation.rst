Installation
============

How to install surfaceS
-----------------------

Downloading
^^^^^^^^^^^

First, clone the github repository.

.. code-block:: bash

    git clone https://github.com/swouf/surfaceS.git

.. _conda: https://anaconda.org/

Install `conda`_
^^^^^^^^^^^^^^^^
.. _install page of conda: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

Download and install conda from the `install page of conda`_.

Create the virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create the virtual environment, execute from the surfaceS folder:

On Windows:

.. code-block:: bash

    conda create --name surfaceS --file surfaceS_pkgs.txt

On linux:

.. code-block:: bash

    conda env create --file surfaceS.yml

Conda should install all the files automatically. However, the procedure is not
fully reliable as it was tested on many systems and it almost never works the
first time.

Move to the newly created environment by using:

.. code-block:: bash

    conda activate surfaceS

If packages are missing, install the following list using conda or
pip.

With conda:

- pip=19.0.3
- pyqt==5.9.2
- matplotlib==3.0.2
- numpy==1.16.2
- pandas==0.24.2
- pyserial=3.4

.. code-block:: bash

    conda install --yes pip=19.0.3 pyqt==5.9.2 matplotlib==3.0.2 numpy==1.16.2 pandas==0.24.2 pyserial=3.4

With pip:

- pyvisa==1.9.1
- logger==1.4

.. code-block:: bash

    pip install pyvisa==1.9.1 logger==1.4

Install the NI backend driver for VISA and the VICP passport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _install page: https://www.ni.com/fr-ch/support/downloads/drivers/download.ni-visa.html

Download from the National Instruments website their backend implementation of
the VISA protocol. You will find it on the NI VISA `install page`_. Install the
software.

Then you will need the VICP passport to be able to communicate with the
Teledyne-Lecroy instruments. Their implementation of the VISA protocol is not
compatible as they added another layer for reliability.

.. _VICP install page: https://teledynelecroy.com/support/softwaredownload/vicppassport.aspx

Go to the `VICP install page`_, download and install the software.

Compile the GUI
^^^^^^^^^^^^^^^
Only when changes have been done to the GUI in the QT Designer

use:
    pyuic5 surfaceS\ui\mainwindow.ui -o surfaceS\ui\mainwindow.py


Start the software
^^^^^^^^^^^^^^^^^^

Start the software using:

.. code-block:: bash

    python ./surfaceS/
