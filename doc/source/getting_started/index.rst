.. _ref_getting_started:

Getting started
###############

.. _ref_software_requirements:

Software requirements
~~~~~~~~~~~~~~~~~~~~~~
.. include:: ../../../README.rst
      :start-after: readme_software_requirements
      :end-before: readme_software_requirements_end


Installation
~~~~~~~~~~~~
.. include:: ../../../README.rst
      :start-after: readme_installation
      :end-before: readme_installation_end


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
