.. _ref_grantami_bomanalytics_api_sustainability_index:

Sustainability API
==================

This section provides an overview of the API for sustainability. The
:ref:`ref_grantami_bomanalytics_api_sustainability_bom` and
:ref:`ref_grantami_bomanalytics_api_sustainability_summary_bom` queries
can be used to determine the environmental performance of a BoM (bill of materials) in Ansys Granta MI 2301 XML BoM
format.

BoM analysis is only performed on items directly defined in the input BoM. Items defined as MI record references might
have associated items defined in the database, but they are not taken into consideration in the analysis.

For more information about BoM item types relevant for sustainability analysis, refer to the
:MI_docs:`BoM item types for Sustainability <rs_and_sustainability/bom_types_sustainability.html>` section of the online
documentation.


.. toctree::
   :maxdepth: 3

   bom
   bom_summary
   common

