.. ref_bom_analytics_api_compliance:

Compliance
==========

Indicators
~~~~~~~~~~
.. py:currentmodule::ansys.granta.bom_analytics.indicators
.. autoclass:: ansys.granta.bom_analytics.indicators.RoHSIndicator
   :members:

   .. automethod:: __init__
   .. autoattribute:: available_flags

.. autoenum:: ansys.granta.bom_analytics.indicators.RoHSFlag

.. autoclass:: ansys.granta.bom_analytics.indicators.WatchListIndicator
   :members:

   .. automethod:: __init__
   .. autoattribute:: available_flags

.. autoenum:: ansys.granta.bom_analytics.indicators.WatchListFlag


Compliance queries
~~~~~~~~~~~~~~~~~~
.. py:currentmodule::ansys.granta.bom_analytics.queries
.. autoclass:: ansys.granta.bom_analytics.queries.SubstanceCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
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

.. autoclass:: ansys.granta.bom_analytics.queries.MaterialCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

.. autoclass:: ansys.granta.bom_analytics.queries.PartCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_part_numbers
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

.. autoclass:: ansys.granta.bom_analytics.queries.SpecificationCompliance
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_specification_ids
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

.. autoclass:: ansys.granta.bom_analytics.queries.BomCompliance
   :members:

   .. automethod:: with_bom
   .. automethod:: with_indicators


Compliance results
~~~~~~~~~~~~~~~~~~
.. py:currentmodule::ansys.granta.bom_analytics._query_results
.. autoclass:: ansys.granta.bom_analytics._query_results.SubstanceComplianceResult
   :members:

   .. autoproperty:: compliance_by_substance_and_indicator
   .. autoproperty:: compliance_by_indicator

.. autoclass:: ansys.granta.bom_analytics._query_results.MaterialComplianceResult
   :members:

   .. autoproperty:: compliance_by_material_and_indicator
   .. autoproperty:: compliance_by_indicator

.. autoclass:: ansys.granta.bom_analytics._query_results.SpecificationComplianceResult
   :members:

   .. autoproperty:: compliance_by_specification_and_indicator
   .. autoproperty:: compliance_by_indicator

.. autoclass:: ansys.granta.bom_analytics._query_results.PartComplianceResult
   :members:

   .. autoproperty:: compliance_by_part_and_indicator
   .. autoproperty:: compliance_by_indicator

.. autoclass:: ansys.granta.bom_analytics._query_results.BomComplianceResult
   :members:

   .. autoproperty:: compliance_by_part_and_indicator
   .. autoproperty:: compliance_by_indicator
