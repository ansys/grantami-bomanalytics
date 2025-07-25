.. _ref_grantami_bomanalytics_api_compliance_indicators:

Indicators
==========
The PyGranta BoM Analytics API can be used to determine compliance against one or more indicators. An indicator
essentially represents a legislation with a threshold. If a substance appears in a certain item, either directly or
indirectly, in a quantity that exceeds that threshold, the item is non-compliant with that indicator. In cases where
the legislation defines a per-substance threshold (for example, RoHS), then this per-substance threshold is used
instead.

Indicators can include a list of legislations, in which case a substance is impacted by the indicator if it is
impacted by one or more legislations included in that indicator.

There are two different types of indicator, and they compute compliance in slightly different ways. It is therefore
important to understand the differences between them. For more information, see
:MI_docs:`Compliance indicators <one_mi/compliance_indicators.html>` in the Granta MI product documentation.


RoHS indicator
--------------

.. autoclass:: ansys.grantami.bomanalytics.indicators.RoHSIndicator

.. autoclass:: ansys.grantami.bomanalytics.indicators.RoHSFlag(value)
   :members:
   :member-order: bysource

Watch list indicator
--------------------

.. autoclass:: ansys.grantami.bomanalytics.indicators.WatchListIndicator

.. autoclass:: ansys.grantami.bomanalytics.indicators.WatchListFlag(value)
   :members:
   :member-order: bysource


.. [1] A substance is determined to be a process chemical if either the substance category is set as 'Used in
   production' or 'May be used in production' in the tabular row where it is referenced, or if the substance is included
   in a material and the material type is set as 'Process' in the tabular row that links the material to a
   specification.
