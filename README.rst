ansys-grantami-bomanalytics
###########################

Project Overview
----------------
PyGranta BoM Analytics is part of the larger `PyAnsys <https://docs.pyansys.com>`_
effort to facilitate the use of Ansys technologies directly from Python.

The MI Restricted Substances and MI Sustainability solutions for Granta MI include REST APIs for:

 - Evaluating compliance of products, assemblies, specifications, and
   materials against legislations.
 - Evaluating the environmental performance of products, assemblies, materials and processes.

This package abstracts automatically-generated code into an easy-to-use client library.


Installation
------------
Install the ``ansys-grantami-bomanalytics`` package with this code:

.. code::

   pip install ansys-grantami-bomanalytics

Alternatively, clone and install this package with this code:

.. code::

   git clone https://github.com/ansys/grantami-bomanalytics
   cd grantami-bomanalytics
   pip install .


Documentation
-------------
The `PyGranta BoM Analytics Documentation <https://bomanalytics.grantami.docs.pyansys.com>`_
provides comprehensive installation and usage information.


Usage
-----
Here's a brief example of how to use PyGranta BoM Analytics:

.. code:: python

    # Connect and query the Granta service.

    >>> from pprint import pprint
    >>> from ansys.grantami.bomanalytics import Connection, queries
    >>> cxn = Connection("http://my_grantami_server/mi_servicelayer").with_autologon().connect()
    >>> query = (
    ...     queries.MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['plastic-abs-pvc-flame'])
    ...     .with_legislation_ids(['Candidate_AnnexXV'])
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
For information on testing, see the ``Contributing`` section of the documentation.


License
-------
PyGranta BoM Analytics is provided under the terms of the MIT license. You can find
this license in the LICENSE file at the root of the repository.
