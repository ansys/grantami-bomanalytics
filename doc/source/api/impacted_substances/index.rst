.. _ref_bom_analytics_api_impactedsubstances_index:

Impacted Substances API
=======================

This section gives an overview of the impacted substances API. The
:ref:`ref_bom_analytics_api_impactedsubstances_materials`,
:ref:`ref_bom_analytics_api_impactedsubstances_specifications`, and
:ref:`ref_bom_analytics_api_impactedsubstances_parts` queries
can be used to determine the substances both directly and indirectly associated with records in a Granta MI database.
The :ref:`ref_bom_analytics_api_impactedsubstances_bom` query accepts a Bill of Materials in Bom1711 XML format, and
returns the substances associated with the records referenced by that Bom.

In all cases, a list of legislations is specified as a list of legislation names.

The quantity of the restricted substance in the parent item is not taken into consideration by these queries. If you
are looking for an analysis of compliance, consider the :ref:`ref_bom_analytics_api_compliance_index`.

.. toctree::
   :maxdepth: 3

   materials
   specifications
   parts
   bom
   common_items