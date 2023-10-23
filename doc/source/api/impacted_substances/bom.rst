.. _ref_grantami_bomanalytics_api_impactedsubstances_bom:

BoM impacted substances
=======================

For more information about BoM item types relevant for impacted substances analysis, refer to the
:MI_docs:`BoM item types for Restricted Substances <rs_and_sustainability/bom_items_rs.html>` section of the online
documentation.

.. _ref_grantami_bomanalytics_api_impactedsubstances_bom_query:

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery
   :inherited-members:
   :exclude-members: api_class

.. _ref_grantami_bomanalytics_api_impactedsubstances_bom_queryresult:

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages
