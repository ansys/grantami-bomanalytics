.. ref_bom_analytics_api_compliance:

Compliance
==========

Indicators
~~~~~~~~~~
.. py:currentmodule::ansys.granta.bom_analytics.indicators
.. autoclass:: ansys.granta.bom_analytics.indicators.RoHSIndicator
   :members:

   .. autoattribute:: available_flags
      :noindex:

.. autoenum:: ansys.granta.bom_analytics.indicators.RoHSFlag

.. autoclass:: ansys.granta.bom_analytics.indicators.WatchListIndicator
   :members:

   .. autoattribute:: available_flags
      :noindex:

.. autoenum:: ansys.granta.bom_analytics.indicators.WatchListFlag


Material Compliance Query
~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.MaterialCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.MaterialComplianceResult
   :members:

   .. autoproperty:: compliance_by_indicator

Material result
---------------

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.MaterialWithComplianceResult
   :members:

   .. autoattribute:: indicators
   .. autoattribute:: substances


Part Compliance Query
~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.PartCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_part_numbers
   .. automethod:: with_batch_size
   .. automethod:: with_indicators


Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.PartComplianceResult
   :members:

   .. autoproperty:: compliance_by_indicator


Part result
-----------

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.PartWithComplianceResult
   :members:

   .. autoattribute:: indicators
   .. autoattribute:: parts
   .. autoattribute:: materials
   .. autoattribute:: specifications
   .. autoattribute:: substances


Specification Compliance Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.SpecificationCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_specification_ids
   .. automethod:: with_batch_size
   .. automethod:: with_indicators


Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.SpecificationComplianceResult
   :members:

   .. autoproperty:: compliance_by_indicator


Specification result
--------------------

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.SpecificationWithComplianceResult
   :members:

   .. autoattribute:: indicators
   .. autoattribute:: specifications
   .. autoattribute:: materials
   .. autoattribute:: coatings
   .. autoattribute:: substances

Coating result
--------------

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.CoatingWithComplianceResult
   :members:

   .. autoattribute:: indicators
   .. autoattribute:: substances


Substance Compliance Query
~~~~~~~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. py:currentmodule::ansys.granta.bom_analytics.queries
.. autoclass:: ansys.granta.bom_analytics.queries.SubstanceCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_cas_numbers
   .. automethod:: with_ec_numbers
   .. automethod:: with_chemical_names
   .. automethod:: with_record_guids_and_amounts
   .. automethod:: with_record_history_guids_and_amounts
   .. automethod:: with_record_history_ids_and_amounts
   .. automethod:: with_cas_numbers_and_amounts
   .. automethod:: with_ec_numbers_and_amounts
   .. automethod:: with_chemical_names_and_amounts
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

Query result
------------

.. py:currentmodule::ansys.granta.bom_analytics._query_results
.. autoclass:: ansys.granta.bom_analytics._query_results.SubstanceComplianceResult
   :members:

   .. autoproperty:: compliance_by_indicator

Substance result
----------------

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.SubstanceWithComplianceResult
   :members:

   .. autoattribute:: indicators


Bom Compliance Query
~~~~~~~~~~~~~~~~~~~~

Query definition
----------------

.. autoclass:: ansys.granta.bom_analytics.queries.BomCompliance
   :members:

   .. automethod:: with_bom
   .. automethod:: with_indicators

Query result
------------

.. autoclass:: ansys.granta.bom_analytics._query_results.BomComplianceResult
   :members:

   .. autoproperty:: compliance_by_indicator
