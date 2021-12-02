.. _ref_bom_analytics_api_compliance_indicators:

Indicators
==========
The BoM Analytics API determines compliance against an Indicator, which can essentially be thought of as a legislation
with a threshold. If a substance appears in a certain item either directly or indirectly in a quantity that exceeds that
threshold as impacted by the legislation, the item is non-compliant with that Indicator. In the case where the
legislation defines a per-substance threshold (e.g. RoHS), then this per-substance threshold will be used instead.

Indicators can include a list of legislations, in which case a substance will be impacted by the indicator if it is
impacted by one or more legislations included in that legislation.

However, there are two different types of indicator that compute compliance in slightly different ways. It is therefore
important to understand the differences between them. For more details, please see the 'Granta MI Restricted Substances
Reports User Guide' that was supplied with the Restricted Substances Reports Bundle.


RoHS Indicator
--------------

.. py:currentmodule::ansys.grantami.bomanalytics.indicators
.. autoclass:: ansys.grantami.bomanalytics.indicators.RoHSIndicator
   :members:

   .. autoattribute:: available_flags
      :noindex:

.. autoenum:: ansys.grantami.bomanalytics.indicators.RoHSFlag


Watch List Indicator
--------------------

.. autoclass:: ansys.grantami.bomanalytics.indicators.WatchListIndicator
   :members:

   .. autoattribute:: available_flags
      :noindex:

.. autoenum:: ansys.grantami.bomanalytics.indicators.WatchListFlag


.. [1] A substance is determined to be a Process Chemical if either the substance category is set as 'Used in
   production' or 'May be used in production' in the tabular row where it is referenced, or if the substance is included in
   a material and the material type is set as 'Process' in the tabular row that links the material to a specification.
