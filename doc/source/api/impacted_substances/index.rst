.. _ref_bom_analytics_api_impactedsubstances_index:

Impacted Substances API
=======================

This section gives an overview of the impacted substances API. The
:ref:`ref_bom_analytics_api_impactedsubstances_materials`,
:ref:`ref_bom_analytics_api_impactedsubstances_specifications`, and
:ref:`ref_bom_analytics_api_impactedsubstances_parts` queries accept a list of references to records in a Granta MI
database and determine the impacted substances both directly and indirectly associated with those records via associated
records in the Granta MI database. The :ref:`ref_bom_analytics_api_impactedsubstances_bom` query is similar, but instead
of records accepts a Bill of Materials in Bom1711 XML format, which in turn includes references to Granta MI records.

In all cases, the impacted substances are determined by a list of legislations, identified by legislation name.

The quantity of the substance in the parent item is not taken into consideration by these queries. If the quentity is
important, i.e. to determine compliance against a legislation that imposes a certain threshold, the
:ref:`ref_bom_analytics_api_compliance_index` should be used instead.

.. toctree::
   :maxdepth: 3

   materials
   specifications
   parts
   bom
   common_items