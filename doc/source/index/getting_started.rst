Getting Started
---------------
To use this package you will require access to a Granta MI server
that includes MI Restricted Substances Reports 2022 R1
or later.

Installation
~~~~~~~~~~~~
The ``ansys.grantami.bomanalytics`` package currently supports Python 3.7 through 3.10 on Windows and Linux.

Install the latest release from `PyPI <https://pypi.org/project/ansys-grantami-bomanalytics/>`_ with:

.. code::

    pip install ansys-grantami-bomanalytics

Alternatively, install the latest from `ansys-grantami-bomanalytics GitHub <https://github.com/pyansys/grantami-bomanalytics>`_ via:

.. code::

    pip install git:https://github.com/pyansys/grantami-bomanalytics.git

For a local "development" version, install with git and poetry:

.. code::

    git clone https://github.com/pyansys/grantami-bomanalytics
    cd grantami-bomanalytics
    poetry install

This allows you to install the ``ansys-grantami-bomanalytics`` package and modify it locally, with
the changes reflected in your Python setup after restarting the Python kernel.

Ansys software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the latest features, you must have a working installation of Ansys Granta MI 2022 R1,
with read access, along with the 2022 R1 MI Restricted Substances Reports Bundle.

Verify your installation
~~~~~~~~~~~~~~~~~~~~~~~~
Check that you can start the BomServices Client from Python by running:

.. code:: python

    >>> from ansys.grantami.bomanalytics import Connection
    >>> connection = Connection("my.server.name").with_autologon().connect()
    >>> print(connection)

    <BomServicesClient: url="my.server.name", dbkey="MI_Restricted_Substances">

If you see a response from the server, congratulations. You're ready
to get started using the BomAnalytics service. For further information
about the available queries see the :ref:`ref_grantami_bomanalytics_examples`.
You can also consult the :ref:`ref_grantami_bomanalytics_api_index` for more
in-depth worked examples.
