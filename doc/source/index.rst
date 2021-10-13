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
Lorem Ipsum


Quick Code
----------
Here's a brief example of how the client works:

.. code:: python

    >>> from ansys.granta.bom_analytics import Connection, queries
        >>> cxn = Connection(servicelayer_url='http://localhost/mi_servicelayer').with_autologon().build()
        >>> query = queries.MaterialImpactedSubstancesQuery().
    >>> cxn = Connection(servicelayer_url='http://localhost/mi_servicelayer').with_autologon().build()
    >>> query = queries.MaterialImpactedSubstances(). \
    ...     with_material_ids(['plastic-abs-pvc-flame', 'stainless-216-annealed']). \
    ...     with_legislations(['REACH - The Candidate List', 'TSCA Section 5(a) SNURS'])
    >>> result = cxn.run(query)
    >>> result.impacted_substances

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
