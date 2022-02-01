.. _ref_grantami_bomanalytics_api_impactedsubstances_bom:

BoM Impacted Substances Query
=============================

.. _ref_grantami_bomanalytics_api_impactedsubstances_bom_query:

Query Definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery
   :members:

   .. automethod:: with_legislations
   .. automethod:: with_bom

.. _ref_grantami_bomanalytics_api_impactedsubstances_bom_queryresult:

Query Result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages

BoM Result
~~~~~~~~~~

The ``BoMWithImpactedSubstancesResult`` object does exist, but it is not documented since it is not exposed by any
public methods. The rationale is as follows:

A single :ref:`ref_grantami_bomanalytics_api_impactedsubstances_bom_query` query can only operate on a single BoM.
Therefore, there is no grouping of impacted substances by BoM, which is what the ``BoMWithImpactedSubstancesResult``
would be used for. :ref:`ref_grantami_bomanalytics_api_impactedsubstances_substances` objects are only available either
as a flat list or grouped by legislation. Both of these views are available on the
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_bom_queryresult` object above.
