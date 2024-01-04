.. _ref_grantami_bomanalytics_api_index:

API reference
=============

The API for PyGranta BoM Analytics is split into different sections. The following sections describe
general functionality that is applicable to both Restricted Substances and Sustainability:

- :ref:`ref_grantami_bomanalytics_common_connection` describes how to connect to Granta MI and, if
  required, configure any schema customizations in the API client. It also explains how to run
  queries.
- :ref:`ref_grantami_bomanalytics_common_messages` describes the structure of log messages
  returned by the Granta MI server.
- :ref:`ref_grantami_bomanalytics_common_exceptions` lists the possible custom exceptions that
  might be raised.
- :ref:`ref_grantami_bomanalytics_batching` explains how queries are batched if they exceed a
  certain size.
- :ref:`ref_grantami_bomanalytics_record_identification` explains how Granta MI records are
  identified throughout the package.
- :ref:`ref_grantami_bomanalytics_bom_helpers_index` explains how to create, read, edit, and save
  Bill of Materials objects for Compliance and Sustainability reporting.

Additionally, the following sections describe how to build queries and interpret results for
different types of analysis:

- :ref:`ref_grantami_bomanalytics_api_impactedsubstances_index`
- :ref:`ref_grantami_bomanalytics_api_compliance_index`
- :ref:`ref_grantami_bomanalytics_api_sustainability_index`


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
