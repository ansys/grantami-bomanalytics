.. _ref_grantami_bomanalytics_api_compliance_index:

Compliance API
==============

The
:ref:`ref_grantami_bomanalytics_api_compliance_substances`,
:ref:`ref_grantami_bomanalytics_api_compliance_materials`,
:ref:`ref_grantami_bomanalytics_api_compliance_specifications`, and
:ref:`ref_grantami_bomanalytics_api_compliance_parts` queries (collectively referred to as
record-based compliance queries) can be used to determine the compliance of records in a Granta MI
database. These queries also consider any additional associated BoM items stored in Granta MI.
For example, if the specified part record contains links to other parts and specifications, these
are included in the analysis.

The :ref:`ref_grantami_bomanalytics_api_compliance_bom` query accepts a BoM (bill of materials) in
XML format and returns the compliance status of the BoM based on the BoM's contents. As opposed to
record-based queries, the BoM compliance analysis only considers items explicitly defined in the
input BoM. It does not follow links to other BoM items as in the record-based queries described
previously.

In both cases, compliance is determined based on a number of
:ref:`ref_grantami_bomanalytics_api_compliance_indicators`. An indicator is a collection of one or
more legislations and a threshold. If a certain record directly or indirectly contains substances
impacted by one of the specified legislations in an amount that exceeds the threshold, the record is
not compliant with that indicator. For more information about possible results, see the definitions
of the indicators.

In general, the result of each query is a recursive BoM (or multi-level BoM) that shows the
compliance status and impacted substances at each level. If you are looking for a simple
determination of the substances indirectly or directly contained within a item represented by a
Granta MI record, consider using the
:ref:`ref_grantami_bomanalytics_api_impactedsubstances_index`.

.. note:: The API documented in this section is only available if you have the MI Restricted
  Substances feature included in your license. A
  :class:`~ansys.grantami.bomanalytics.LicensingException` is raised if the feature is not
  available.

.. toctree::
   :maxdepth: 3

   parts
   specifications
   materials
   substances
   bom
   indicators

