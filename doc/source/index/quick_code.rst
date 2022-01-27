Quick Code
----------
Here's a brief example of how the package works. This example finds the
percentage content of all SVHCs in an ABS/PVC blend:

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

1. Connect to Granta MI.
2. Create the appropriate query, choosing between:

   - *Query type*: Compliance or impacted substances
   - *Reference type*: Materials, parts, specifications, substances, or an XML BoM

3. Specify the legislations and records of interest.
4. Run the query.
5. Process the results.
