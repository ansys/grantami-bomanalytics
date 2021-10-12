.. _ref_bom_analytics_api_compliance_index:

Compliance API
==============

This section gives an overview of the compliance API. The
:ref:`ref_bom_analytics_api_compliance_substances`,
:ref:`ref_bom_analytics_api_compliance_materials`,
:ref:`ref_bom_analytics_api_compliance_specifications`, and
:ref:`ref_bom_analytics_api_compliance_parts` queries
can be used to determine compliance of records in a Granta MI database based on a number of
:ref:`ref_bom_analytics_api_compliance_indicators`. An indicator is a collection of one or more legislations and a
threshold; if a certain record directly or indirectly contains substances impacted by one of the specified legislations
in an amount that exceeds the threshold, the record is not compliant with that indicator. See the definitions of the
indicators for more details on the possible results.

The :ref:`ref_bom_analytics_api_compliance_bom` query accepts a Bill of Materials in Bom1711 XML format, and
returns the compliance status of the Bom based on the Granta MI records referenced by it.

The result of each query is in general a recursive BoM (or multi-level BoM) that shows the compliance and impacted
substances at each level. If you are looking for a simple determination of the substances indirectly or directly
contained within a item represented by a Granta MI record, consider the
:ref:`ref_bom_analytics_api_impactedsubstances_index`.

.. toctree::
   :maxdepth: 3

   indicators
   substances
   materials
   specifications
   parts
   bom
