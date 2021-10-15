PyGranta Restricted Substances Compliance API Documentation
===========================================================

.. toctree::
   :hidden:
   :maxdepth: 3

   api/index
   contributing


Introduction and Purpose
------------------------
This project is part of the larger PyAnsys effort to facilitate the use
of Ansys technologies directly from within Python.

The Granta MI Restricted Substances solution includes a REST API for
evaluating compliance of products, assemblies, specifications and
materials against legislations. This package abstracts automatically-
generated code into an easy-to-use client library.


Background
----------
TODO


Quick Code
----------
Here's a brief example of how the package works:

.. code:: python

    >>> from pprint import pprint
    >>> from ansys.granta.bom_analytics import Connection, queries
    >>> cxn = Connection(servicelayer_url='http://localhost/mi_servicelayer').with_autologon().build()
    >>> query = (
    >>>     queries.MaterialImpactedSubstancesQuery()
    >>>     .with_material_ids(['plastic-abs-pvc-flame'])
    >>>     .with_legislations(['REACH - The Candidate List'])
    >>> )
    >>>
    >>> result = cxn.run(query)
    >>> pprint(result.impacted_substances)
    [<ImpactedSubstance: {"cas_number": 10108-64-2, "percent_amount": 1.9}>,
     <ImpactedSubstance: {"cas_number": 107-06-2, "percent_amount": None}>,
     <ImpactedSubstance: {"cas_number": 115-96-8, "percent_amount": 15.0}>,
    ...

The first step is to establish the connection to Granta MI. Then the query is created by first picking the type of
query, in this case a query to find the substances impacting one or more materials, and then adding the materials and
legislations of interest.

Finally, run the query using the connection, which returns the results.


API Reference
~~~~~~~~~~~~~
For full details of the API available see the API reference: :ref:`ref_bom_analytics_api_index`.

Project Index
*************

* :ref:`genindex`
