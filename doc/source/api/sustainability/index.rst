.. _ref_grantami_bomanalytics_api_sustainability_index:

Sustainability API
==================

The :ref:`ref_grantami_bomanalytics_api_sustainability_bom` and
:ref:`ref_grantami_bomanalytics_api_sustainability_summary_bom` queries can be used to determine the
environmental performance of a BoM (bill of materials) in Ansys Granta MI 23/01 or 24/12 XML BoM format.

The BoM analysis only considers items explicitly defined in the input BoM. It does not follow links
to other BoM items as in the record-based queries available for Impacted Substances and Compliance
analysis.

For more information about BoM item types relevant for sustainability analysis, see
:MI_docs:`Item types for Sustainability <one_mi/bom_types_sustainability.html>` in the Granta
MI product documentation.

.. note:: The API documented in this section is only available if you have the MI Restricted
  Substances feature included in your license. A
  :class:`~ansys.grantami.bomanalytics.LicensingException` will be raised if the feature is not
  available.

.. versionadded:: 2.0

.. toctree::
   :maxdepth: 3

   bom
   bom_summary
   common

