Installation
============

Installing the ASpecD package is as simple as installing any other Python package, as ASpecD is available from the `Python Package Index (PyPI) <https://www.pypi.org/>`_. Simply open a terminal on your computer and type::

  pip install aspecd

This will install the ASpecD package (and all its dependencies) on your computer.

Of course, you need to have Python (and pip) installed before you can use the above command, and it is always advisable to install packages in a **virtual environment** of their own.

Hence, a more thorough sequence of events would be:

#. Install Python (if it is not already installed on your system).

#. Create a Python virtual environment for ASpecD.

#. Activate the newly created virtual environment.

#. Install ASpecD therein, using the above command.

A few details for all these steps are given below.


Installing Python
-----------------

For how to install Python on your system, see the `official documentation <https://wiki.python.org/moin/BeginnersGuide/Download>`_. Linux users: you will most certainly have Python installed already.


Create a Python virtual environment
-----------------------------------

It is good practice to always use virtual environments when working with Python. One reason: On some operating systems, crucial tasks depend on Python, and installing Python packages globally may interfere with the system.

The good news: Creating Python virtual environments is fairly simple:

.. code-block:: bash

    python -m venv aspecd

This will create a Python virtual environment named ``aspecd`` in the current directory. Of course, you can give your virtual environment any name you like. However, be careful with spaces and special characters, depending on your system.


Activate the newly created virtual environment
----------------------------------------------

A Python virtual environment needs to be activated. This is usually done using the following command:

.. code-block:: bash

    source aspecd/bin/activate

Assuming in this case that your virtual environment is called ``aspecd`` and that you are in the same path where you just created your virtual environment.

Deactivating is simple as well, once you are done. Either close the terminal, or issue the command ``deactivate``.


Install ASpecD
--------------

Once you activated your virtual environment where you want to install the ASpecD framework in, proceed as given above:

.. code-block:: bash

    pip install aspecd

This will download the ASpecD framework from the `Python Package Index (PyPI) <https://www.pypi.org/>`_ and install it locally. All dependencies will be installed as well.


.. note::

    The above instructions assume a fairly standard Python installation using pip. Of course, there are other Python distributions available as well, such as conda. If you are using such a Python distribution, pip should be available as well. However, in case of problems consult the documentation of your respective Python distribution for details.

