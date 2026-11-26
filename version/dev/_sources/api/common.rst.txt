.. _ref_grantami_bomanalytics_common_connection:

Common
======

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
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.LogMessage


.. _ref_grantami_bomanalytics_common_exceptions:

Exceptions
~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.GrantaMIException

.. autoclass:: ansys.grantami.bomanalytics.LicensingException


Value with unit
~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.ValueWithUnit
   :members:

Record references
~~~~~~~~~~~~~~~~~

See :ref:`ref_grantami_bomanalytics_record_identification` for more information about populated
properties on record reference objects.

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.PartReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.SpecificationReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.MaterialReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.CoatingReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.ProcessReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.SubstanceReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source

.. autoclass:: ansys.grantami.bomanalytics._item_definitions.TransportReference
   :members:
   :inherited-members:
   :member-order: by_mro_by_source
