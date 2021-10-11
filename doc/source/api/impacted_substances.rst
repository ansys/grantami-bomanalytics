.. ref_bom_analytics_api_impacted_substances:

Impacted Substances
===================

Impacted substances queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. py:currentmodule::ansys.granta.bom_analytics.queries
.. autoclass:: ansys.granta.bom_analytics.queries.MaterialImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

.. autoclass:: ansys.granta.bom_analytics.queries.PartImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_part_numbers
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

.. autoclass:: ansys.granta.bom_analytics.queries.SpecificationImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_specification_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

.. autoclass:: ansys.granta.bom_analytics.queries.BomImpactedSubstances
   :members:

   .. automethod:: with_bom
   .. automethod:: with_legislations


Impacted substances results
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. py:currentmodule::ansys.granta.bom_analytics._query_results
.. autoclass:: ansys.granta.bom_analytics._query_results.MaterialImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_material_and_legislation
   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

.. autoclass:: ansys.granta.bom_analytics._query_results.SpecificationImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_specification_and_legislation
   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

.. autoclass:: ansys.granta.bom_analytics._query_results.PartImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_part_and_legislation
   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

.. autoclass:: ansys.granta.bom_analytics._query_results.BomImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances
