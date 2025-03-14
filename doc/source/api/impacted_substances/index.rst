.. _ref_grantami_bomanalytics_api_impactedsubstances_index:

Impacted substances API
=======================

The :ref:`ref_grantami_bomanalytics_api_impactedsubstances_materials`,
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_specifications`, and
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_parts` queries (collectively referred to as
record-based impacted substances queries) accept a list of references to records in a Granta MI
database. These queries also consider any additional associated BoM items stored in Granta MI.
For example, if the specified part record contains links to other parts and specifications, these
are included in the analysis.

The :ref:`ref_grantami_bomanalytics_api_impactedsubstances_bom` BoM-based query accepts a
Bill of Materials in XML format, which includes references to Granta MI records. As opposed to
record-based queries, the BoM-based impacted substances analysis only considers items explicitly
defined in the input BoM. It does not follow links to other BoM items as in the record-based queries
described previously.

In both cases, impacted substances are determined by a list of legislations, identified by
legislation ID.

These queries do not take the quantity of the substance in the parent item into consideration. If
the quantity is important, for example to determine compliance against a legislation that imposes a
certain threshold, you should use the :ref:`ref_grantami_bomanalytics_api_compliance_index` instead.

.. note:: The API documented in this section is only available if you have the MI Restricted
  Substances feature included in your license. A
  :class:`~ansys.grantami.bomanalytics.LicensingException` is raised if the feature is not
  available.

.. toctree::
   :maxdepth: 3

   parts
   specifications
   materials
   bom
   impacted_substances
