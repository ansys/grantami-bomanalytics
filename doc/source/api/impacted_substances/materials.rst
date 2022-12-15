.. _ref_grantami_bomanalytics_api_impactedsubstances_materials:

Material impacted substances
============================

Query definition
~~~~~~~~~~~~~~~~

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

.. autoclass:: ansys.grantami.bomanalytics._query_results.MaterialImpactedSubstancesQueryResult
   :members:
   :exclude-members: impacted_substances_by_material

   .. autoattribute:: impacted_substances_by_material
   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages

Material result
~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.MaterialWithImpactedSubstancesResult
