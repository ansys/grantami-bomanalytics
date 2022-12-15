ansys-grantami-bomanalytics
###########################

Project Overview
----------------
Granta MI BoM Analytics is part of the larger `PyAnsys <https://github.com/pyansys>`_
effort to facilitate the use of Ansys technologies directly from Python.

The Granta MI Restricted Substances solution includes a REST API for
evaluating compliance of products, assemblies, specifications, and
materials against legislations. This package abstracts automatically-
generated code into an easy-to-use client library.


Installation
------------
Install the ``ansys-grantami-bomanalytics`` package with this code:

.. code::

   pip install ansys-grantami-bomanalytics

Alternatively, clone and install thie package with this code:

.. code::

   git clone https://github.com/pyansys/grantami-bomanalytics
   cd grantami-bomanalytics
   pip install .


Documentation
-------------
The `Granta MI BoM Analytics Documentation <https://grantami.docs.pyansys.com>`_
provides comprehensive installation and usage information.


Usage
-----
Here's a brief example of how to use Granta MI BoM Analytics:

.. code:: python

    # Connect and query the Granta service.

    >>> from pprint import pprint
    >>> from ansys.grantami.bomanalytics import Connection, queries
    >>> cxn = Connection("http://my_grantami_server/mi_servicelayer").with_autologon().connect()
    >>> query = (
    ...     queries.MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['plastic-abs-pvc-flame'])
    ...     .with_legislations(['REACH - The Candidate List'])
    ... )

    # Print out the result from the query.

    >>> result = cxn.run(query)
    >>> pprint(result.impacted_substances)
    [<ImpactedSubstance: {"cas_number": 10108-64-2, "percent_amount": 1.9}>,
     <ImpactedSubstance: {"cas_number": 107-06-2, "percent_amount": None}>,
     <ImpactedSubstance: {"cas_number": 115-96-8, "percent_amount": 15.0}>,
    ...


Testing
-------
For information on testing, see `Contributing <https://grantami.docs.pyansys.com/contributing>`_.


License
-------
Granta MI BoM Analytics is provided under the terms of the MIT license. You can find
this license in the LICENSE file at the root of the repository.
