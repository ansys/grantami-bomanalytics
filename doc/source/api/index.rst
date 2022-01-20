.. _ref_grantami_bomanalytics_api_index:

API Reference
=============

The BoM Analytics API is split into three key sections, as shown below. The
:ref:`ref_grantami_bomanalytics_common_connection` section describes how to connect to Granta MI, and, if required,
configure any schema customizations in the API client. It also explains how to run queries.

The :ref:`ref_grantami_bomanalytics_api_impactedsubstances_index` and
:ref:`ref_grantami_bomanalytics_api_compliance_index` sections then explain how to build specific queries and how to
interpret the results.

The :ref:`ref_grantami_bomanalytics_common_messages` section describes the structure of log messages returned by the
Granta MI server, and the :ref:`ref_grantami_bomanalytics_common_exceptions` section lists the possible custom
exceptions that may be raised by this package.

Some of the examples given in the API Reference may use different classes than the one being documented. In all cases,
both classes are equivalent in terms of the functionality being demonstrated.

.. toctree::
   :maxdepth: 2

   common
   batching
   impacted_substances/index
   compliance/index
