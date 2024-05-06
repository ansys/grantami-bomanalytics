.. _ref_grantami_bomanalytics_bom_api:

BoM object model
================

The models documented in this section are Python bindings for the Ansys Granta MI 23/01 XML schema.
Not all elements are required to define a valid BoM for analysis, and not all elements have an impact
on all types of analysis. For information on the relevant items for each analysis type,
see :ref:`ref_grantami_bomanalytics_api_index`.

.. note::
   The following elements are defined in the 23/01 BoM schema but are not supported in this module:

   * ``NonMIPartReference`` on :class:`~ansys.grantami.bomanalytics.bom_types._bom_types.Part`
   * ``Annotations`` and ``AnnotationSources`` on :class:`~ansys.grantami.bomanalytics.bom_types._bom_types.BillOfMaterials`

   This module does not contain classes that correspond to these types and cannot serialize a BoM that includes these
   elements. It is still possible to deserialize an XML BoM that uses these elements, but these elements cannot be
   converted to Python objects.

.. versionadded:: 2.0

.. _ref_grantami_bomanalytics_api_billofmaterials:
.. autoclass:: ansys.grantami.bomanalytics.bom_types._bom_types.BillOfMaterials
   :inherited-members:
   :member-order: bysource


.. automodule:: ansys.grantami.bomanalytics.bom_types._bom_types
   :exclude-members: BillOfMaterials, BaseType, HasNamespace, SupportsCustomFields
   :inherited-members:
   :member-order: bysource
