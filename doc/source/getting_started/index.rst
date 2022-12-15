.. _ref_getting_started_grantami_bomanalytics:

Getting started
---------------
To use the ``ansys.grantami.bomanalytics`` package, you must have access to a
Granta MI server that includes MI Restricted Substances Reports 2022 R1
or later.

The ``ansys.grantami.bomanalytics`` package currently supports Python 3.7
through 3.10 on Windows and Linux.

Installation
~~~~~~~~~~~~
To install the latest release from `PyPI <https://pypi.org/project/ansys-grantami-bomanalytics/>`_, use
this code:

.. code::

    pip install ansys-grantami-bomanalytics


Alternatively, to install the latest from `ansys-grantami-bomanalytics GitHub <https://github.com/pyansys/grantami-bomanalytics>`_,
use this code:

.. code::

    pip install git:https://github.com/pyansys/grantami-bomanalytics.git


To install a local *development* version with Git and Poetry, use this code:

.. code::

    git clone https://github.com/pyansys/grantami-bomanalytics
    cd grantami-bomanalytics
    poetry install


The preceding code installs the package and allows you to modify it locally,
with your changes reflected in your Python setup after restarting the Python kernel.

Ansys software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the latest features, you must have a working installation of Ansys Granta MI 2022 R1
or later with read access, along with an 2022 R1 or later installation of the MI Restricted
Substances Reports Bundle.

Verify your installation
~~~~~~~~~~~~~~~~~~~~~~~~
Check that you can start the BomServices Client from Python by running this code:

.. code:: python

    >>> from ansys.grantami.bomanalytics import Connection
    >>> connection = Connection("my.server.name").with_autologon().connect()
    >>> print(connection)

    <BomServicesClient: url="my.server.name", dbkey="MI_Restricted_Substances">

If you see a response from the server, congratulations. You can start using
the BomAnalytics service. For information about available queries,
see :ref:`ref_grantami_bomanalytics_examples`. For more in-depth descriptions,
consult :ref:`ref_grantami_bomanalytics_api_index`.
