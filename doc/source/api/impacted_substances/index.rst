.. _ref_grantami_bomanalytics_api_impactedsubstances_index:

Impacted Substances API
=======================

This section gives an overview of the Impacted Substances API. The
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_materials`,
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_specifications`, and
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_parts` queries accept a list of references to records in a
Granta MI database and determine the impacted substances that are directly or indirectly associated with these records via
associated records in the Granta MI database. The :ref:`ref_grantami_bomanalytics_api_impactedsubstances_bom` query is
similar, but instead of records it accepts a Bill of Materials in Ansys Granta MI 1711 XML BoM format, which in turn includes references to
Granta MI records.

In all cases, impacted substances are determined by a list of legislations, identified by legislation name.

These queries do not take the quantity of the substance in the parent item into consideration. If the quantity is
important, for example to determine compliance against a legislation that imposes a certain threshold, you should
use the :ref:`ref_grantami_bomanalytics_api_compliance_index` instead.

.. toctree::
   :maxdepth: 3

   parts
   specifications
   materials
   bom
   impacted_substances
