.. _ref_grantami_bomanalytics_api_impactedsubstances_materials:

Material Impacted Substances
============================

Query Definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.MaterialImpactedSubstancesQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query Result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.MaterialImpactedSubstancesQueryResult
   :members:
   :exclude-members: impacted_substances_by_material

   .. autoattribute:: impacted_substances_by_material
   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages

Material Result
~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.MaterialWithImpactedSubstancesResult
