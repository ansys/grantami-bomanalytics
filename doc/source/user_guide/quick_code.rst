Quick code
==========

To show how the ``grantami-bomanalytics`` package works, this brief compliance example
shows how to find the percentage content of all SVHCs (substances of very
high concern) in an ABS/PVC blend:

.. code:: python

    >>> from pprint import pprint
    >>> from ansys.grantami.bomanalytics import Connection, queries
    >>> cxn = Connection(servicelayer_url="http://my_mi_server/mi_servicelayer") \
    ...     .with_autologon().connect()
    >>> query = (
    ...     queries.MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['plastic-abs-pvc-flame'])
    ...     .with_legislation_ids(['Candidate_AnnexXV'])
    ... )
    >>> result = cxn.run(query)
    >>> pprint(result.impacted_substances)
    [<ImpactedSubstance: {"cas_number": 10108-64-2, "percent_amount": 1.9}>,
     <ImpactedSubstance: {"cas_number": 107-06-2, "percent_amount": None}>,
     <ImpactedSubstance: {"cas_number": 115-96-8, "percent_amount": 15.0}>,
    ...


The sequence of events is as follows:

#. Connect to Granta MI.
#. Create the appropriate query with the relevant parameters and references
   (see :ref:`ref_grantami_bomanalytics_api_index` for more details).
#. Run the query.
#. Process the results.