.. _ref_grantami_bomanalytics_api_compliance_index:

Compliance API
==============

This section provides an overview of the API for compliance. The
:ref:`ref_grantami_bomanalytics_api_compliance_substances`,
:ref:`ref_grantami_bomanalytics_api_compliance_materials`,
:ref:`ref_grantami_bomanalytics_api_compliance_specifications`, and
:ref:`ref_grantami_bomanalytics_api_compliance_parts` queries
can be used to determine the compliance of records in a Granta MI database based on a number of
:ref:`ref_grantami_bomanalytics_api_compliance_indicators`. An indicator is a collection of one or more legislations and
a threshold. If a certain record directly or indirectly contains substances impacted by one of the specified
legislations in an amount that exceeds the threshold, the record is not compliant with that indicator. For more
information about possible results, see the definitions of the indicators.

The :ref:`ref_grantami_bomanalytics_api_compliance_bom` query accepts a BoM (bill of materials) in Ansys Granta MI 1711 XML BoM format and
returns the compliance status of the BoM based on the Granta MI records referenced by it.

In general, the result of each query is a recursive BoM (or multi-level BoM) that shows the compliance status and impacted
substances at each level. If you are looking for a simple determination of the substances indirectly or directly
contained within a item represented by a Granta MI record, consider using the
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_index`.

.. toctree::
   :maxdepth: 3

   parts
   specifications
   materials
   substances
   bom
   indicators

