.. _ref_grantami_bomanalytics_api_index:

API reference
=============

The API for PyGranta BoM Analytics is split into these key sections:

- :ref:`ref_grantami_bomanalytics_common_connection` describes how to connect to Granta MI and, if required,
  configure any schema customizations in the API client. It also explains how to run queries.
- :ref:`ref_grantami_bomanalytics_common_messages` describes the structure of log messages returned by the
  Granta MI server.
- :ref:`ref_grantami_bomanalytics_common_exceptions` lists the possible custom exceptions that might be
  raised.
- :ref:`ref_grantami_bomanalytics_batching` explains how queries are batched if they exceed a certain size.  
- :ref:`ref_grantami_bomanalytics_record_identification` explains how Granta MI records are identified throughout the
  package.
- :ref:`ref_grantami_bomanalytics_api_impactedsubstances_index` explains how to build queries for impacted
  substances and interpret results.
- :ref:`ref_grantami_bomanalytics_api_compliance_index` explains how to build queries for compliance
  and how to interpret results.
- :ref:`ref_grantami_bomanalytics_api_sustainability_index` explains how to build queries for sustainability
  and how to interpret results.
- :ref:`ref_grantami_bomanalytics_bom_helpers_index` explains how to create, read, edit, and save Bill of Materials
  objects for Compliance and Sustainability reporting.

.. note::
   While some examples use a different class than the one being documented, both classes are always
   equivalent in terms of the capability being demonstrated.

.. toctree::
   :maxdepth: 2

   common
   batching
   record_identification
   impacted_substances/index
   compliance/index
   sustainability/index
   bom_builder/index
