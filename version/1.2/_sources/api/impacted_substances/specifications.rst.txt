.. _ref_grantami_bomanalytics_api_impactedsubstances_specifications:

Specification impacted substances
=================================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.SpecificationImpactedSubstancesQuery
   :members:

   .. automethod:: with_legislations
   .. automethod:: with_specification_ids
   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_batch_size

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.SpecificationImpactedSubstancesQueryResult
   :members:
   :exclude-members: impacted_substances_by_specification

   .. autoattribute:: impacted_substances_by_specification
   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages

Specification result
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SpecificationWithImpactedSubstancesResult
