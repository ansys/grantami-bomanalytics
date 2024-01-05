.. _ref_grantami_bomanalytics_api_index:

API reference
=============

The API for PyGranta BoM Analytics is split into different sections. The following sections describe
general capabilities applicable to both restricted substances and sustainability:

- :ref:`ref_grantami_bomanalytics_common_connection` describes how to connect to Granta MI and, if
  required, configure any schema customizations in the API client. It also explains how to run
  queries.
- :ref:`ref_grantami_bomanalytics_common_messages` describes the structure of log messages
  returned by the Granta MI server.
- :ref:`ref_grantami_bomanalytics_common_exceptions` lists the possible custom exceptions that
  might be raised.
- :ref:`ref_grantami_bomanalytics_batching` explains how queries are batched if they exceed a
  certain size.
- :ref:`ref_grantami_bomanalytics_query_type_differences` explains some key differences between
  record-based and BoM-based queries, including how records are identified and how additional
  items are included in the analysis.
- :ref:`ref_grantami_bomanalytics_bom_helpers_index` explains how to create, read, edit, and save
  BoM objects for restricted substances and sustainability analysis.

The following sections describe how to build queries and interpret results for different types of
analysis:

- :ref:`ref_grantami_bomanalytics_api_impactedsubstances_index`
- :ref:`ref_grantami_bomanalytics_api_compliance_index`
- :ref:`ref_grantami_bomanalytics_api_sustainability_index`


.. note::
   While some examples use a different class than the one being documented, both classes are always
   equivalent in terms of the capability being demonstrated.

.. toctree::
   :maxdepth: 2
   :hidden:

   common
   batching
   query_type_differences
   impacted_substances/index
   compliance/index
   sustainability/index
   bom_builder/index
