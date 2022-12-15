Granta MI BoM Analytics |version|
=================================

.. toctree::
   :hidden:
   :maxdepth: 3

   getting_started/index
   api/index
   examples/index
   contributing


Introduction
------------
This project is part of the larger PyAnsys effort to facilitate the use
of Ansys technologies directly from within Python.

Granta MI provides a mature and feature-rich method for managing
compliance data as part of the Restricted Substances solution.
When combined with the Granta MI BoM Analyzer and Restricted Substances
Reports, the data managed in Granta MI can be leveraged to
determine compliance for complex specification hierarchies, assemblies,
and even entire products.

The ``grantami-bomanalytics`` package takes the functionality available
interactively through the web Granta MI browser and exposes it as an API.
The expected use cases for this package are as follows:

- Rolling up compliance results periodically and storing these results
  in Granta MI.
- Scripting compliance calculations as part of a release process.
- Allowing compliance to be determined for BoMs (Bills of Materials) stored
  in third-party systems, such as PLM or ERP systems.

Background
----------
The Granta MI Restricted Substances solution includes a REST API for
evaluating compliance of products, assemblies, specifications, and
materials against legislations. This package automatically abstracts
generated code into an easy-to-use client library.

Dependencies
------------
To use the ``grantami-bomanalytics`` package, you must have access
to a Granta MI server that includes MI Restricted Substances Reports
2022 R1 or later. This package also has the following Python package
dependencies:

- ``ansys-grantami-bomanalytics-openapi`` package
- ``ansys-openapi-common`` package

These package dependencies are installed automatically by
`pip <https://github.com/pypa/pip>`_, the package installer for
Python. For more information, see the installation information
in :ref:`_ref_getting_started_grantami_bomanalytics`.

Quick code
----------
To show how the ``grantami-bomanalytics`` package works, this brief example
shows how to find the percentage content of all SVHCs (substances of very
high concern) in an ABS/PVC blend:

.. code:: python

    >>> from pprint import pprint
    >>> from ansys.grantami.bomanalytics import Connection, queries
    >>> cxn = Connection(servicelayer_url="http://localhost/mi_servicelayer") \
    ...     .with_autologon().connect()
    >>> query = (
    ...     queries.MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['plastic-abs-pvc-flame'])
    ...     .with_legislations(['REACH - The Candidate List'])
    ... )
    >>> result = cxn.run(query)
    >>> pprint(result.impacted_substances)
    [<ImpactedSubstance: {"cas_number": 10108-64-2, "percent_amount": 1.9}>,
     <ImpactedSubstance: {"cas_number": 107-06-2, "percent_amount": None}>,
     <ImpactedSubstance: {"cas_number": 115-96-8, "percent_amount": 15.0}>,
    ...


The sequence of events is as follows:

#. Connect to Granta MI.
#. Create the appropriate query, choosing between:

   - Query type: Compliance or impacted substances
   - Reference type: Materials, parts, specifications, substances, or an XML BoM

#. Specify the legislations and records of interest.
#. Run the query.
#. Process the results.

API reference
-------------
For comprehensive API documentation, see :ref:`ref_grantami_bomanalytics_api_index`.

Contributing
------------
Contributions to Granta MI BoM Analytics are welcomed. For more information, see
:doc:`Contributing<contributing>`.

Project index
-------------

* :ref:`genindex`
