.. _ref_grantami_bomanalytics_common_connection:

Granta MI connection
====================

Connection builder
~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.Connection
   :members:

   .. automethod:: with_autologon
   .. automethod:: with_credentials
   .. automethod:: with_oidc
   .. automethod:: with_anonymous


BoM Analytics client
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._connection.BomAnalyticsClient
   :members:

.. _ref_grantami_bomanalytics_common_messages:

Log messages
============

.. autoclass:: ansys.grantami.bomanalytics._query_results.LogMessage


.. _ref_grantami_bomanalytics_common_exceptions:

Exceptions
==========

.. autoclass:: ansys.grantami.bomanalytics.GrantaMIException
