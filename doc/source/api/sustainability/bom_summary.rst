.. _ref_grantami_bomanalytics_api_sustainability_summary_bom:

BoM sustainability summary
==========================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomSustainabilitySummaryQuery
   :members:

   .. automethod:: with_bom
   .. automethod:: with_units

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomSustainabilitySummaryQueryResult
   :members:
   :inherited-members:


Phase summary
~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SustainabilityPhaseSummaryResult
   :members:
   :inherited-members:


Transport
~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.TransportSummaryResult
   :members:
   :inherited-members:
   :exclude-members: record_reference

Material
~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.MaterialSummaryResult
   :members:
   :inherited-members:
   :exclude-members: record_reference

.. autoclass:: ansys.grantami.bomanalytics._item_results.ContributingComponentResult
   :members:
   :inherited-members:
   :exclude-members: record_reference

Process
~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.ProcessSummaryResult
   :members:
   :inherited-members:
   :exclude-members: record_reference

