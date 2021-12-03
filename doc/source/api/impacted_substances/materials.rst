.. _ref_bom_analytics_api_impactedsubstances_materials:

Material Impacted Substances
============================

Query definition
~~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.grantami.bomanalytics.queries
.. autoclass:: ansys.grantami.bomanalytics.queries.MaterialImpactedSubstancesQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
~~~~~~~~~~~~

.. py:currentmodule::ansys.grantami.bomanalytics._query_results
.. autoclass:: ansys.grantami.bomanalytics._query_results.MaterialImpactedSubstancesQueryResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Material result
~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.grantami.bomanalytics._item_results
.. autoclass:: ansys.grantami.bomanalytics._item_results.MaterialWithImpactedSubstancesResult
   :members:

   .. autoattribute:: material_id
   .. autoattribute:: record_guid
   .. autoattribute:: record_history_guid
   .. autoattribute:: record_history_identity
   .. autoattribute:: substances_by_legislation
   .. autoattribute:: substances
