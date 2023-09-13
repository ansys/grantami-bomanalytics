.. _ref_grantami_bomanalytics_api_sustainability_bom:

BoM sustainability
==================


Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomSustainabilityQuery
   :members:

   .. automethod:: with_bom
   .. automethod:: with_units

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomSustainabilityQueryResult
   :members:
   :inherited-members:

Part
~~~~
.. autoclass:: ansys.grantami.bomanalytics._item_results.PartWithSustainabilityResult

Transport
~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.TransportWithSustainabilityResult

Material
~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.MaterialWithSustainabilityResult

Process
~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.ProcessWithSustainabilityResult

Specification
~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SpecificationWithSustainabilityResult

Coating
~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.CoatingResult

Substance
~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SubstanceResult
