.. ref_bom_analytics_api_impacted_substances:

Impacted Substances
===================

Material Impacted Substances Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. py:currentmodule::ansys.granta.bom_analytics.queries
.. autoclass:: ansys.granta.bom_analytics.queries.MaterialImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
------------

.. py:currentmodule::ansys.granta.bom_analytics._query_results
.. autoclass:: ansys.granta.bom_analytics._query_results.MaterialImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Material result
---------------

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.MaterialWithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations


Part Impacted Substances Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.PartImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_part_numbers
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.PartImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Part result
-----------

.. autoclass:: ansys.granta.bom_analytics._item_results.PartWithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations


Specification Impacted Substances Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.SpecificationImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_specification_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.SpecificationImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances


Specification result
--------------------

.. autoclass:: ansys.granta.bom_analytics._item_results.SpecificationWithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations


Bom Impacted Substances Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.BomImpactedSubstances
   :members:

   .. automethod:: with_bom
   .. automethod:: with_legislations

Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.BomImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Bom result
----------

.. autoclass:: ansys.granta.bom_analytics._item_results.BoM1711WithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations


Common item results
~~~~~~~~~~~~~~~~~~~

Impacted substance result
-------------------------

.. autoclass:: ansys.granta.bom_analytics._item_results.ImpactedSubstance
   :members:

Legislation result
------------------

.. autoclass:: ansys.granta.bom_analytics._item_results.LegislationResult
   :members:
