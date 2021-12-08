Ansys Granta MI Bom Analytics API Documentation
===============================================

.. toctree::
   :hidden:
   :maxdepth: 3

   api/index
   contributing


Introduction and Purpose
------------------------
This project is part of the larger PyAnsys effort to facilitate the use
of Ansys technologies directly from within Python.

Granta MI provides a mature and feature-rich method for managing
compliance data as part of the Restricted Substances solution.
When combined with the Bom Analyzer and the Restricted Substances
reporting bundle, the data managed in Granta MI can be leveraged to
determine compliance for complex specification hierarchies, assemblies,
and even entire products.

This package takes the functionality available interactively through
the web browser, and exposes it as an API. The expected use cases
for this package are as follows:

- Periodically rolling up compliance results and storing the results
  in Granta MI
- Scripting compliance calculations as part of a release process
- Allowing compliance to be determined for BoMs stored in third-party
  systems, for example PLM or ERP systems


Dependencies
------------
To use this package you will require access to a Granta MI server
that includes the MI Restricted Substances Reports version 2022R1
or later.


Background
----------
The Granta MI Restricted Substances solution includes a REST API for
evaluating compliance of products, assemblies, specifications and
materials against legislations. This package abstracts automatically-
generated code into an easy-to-use client library.


Quick Code
----------
Here's a brief example of how the package works. This example finds the
percentage content of all SVHCs in an ABS/PVC blend:

.. code:: python

    >>> from pprint import pprint
    >>> from ansys.grantami.bomanalytics import Connection, queries
    >>> cxn = Connection(servicelayer_url="http://localhost/mi_servicelayer") \
    ...     .with_autologon().build()
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

1. Connect to Granta MI.
2. Create the appropriate query, choosing between:

   - *Query type*: Compliance or impacted substances.
   - *Reference type*: Materials, parts, specifications, substances, or an XML BoM.

3. Specify the legislations and records of interest.
4. Run the query.
5. Process the results.


API Reference
-------------
For full details of the API available see the API reference: :ref:`ref_bom_analytics_api_index`.

Project Index
-------------

* :ref:`genindex`
