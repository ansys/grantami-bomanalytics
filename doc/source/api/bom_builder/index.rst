.. _ref_grantami_bomanalytics_bom_helpers_index:

BoM helpers
===========

BoM helpers represent a BoM (bill of materials) in Ansys Granta MI 23/01, 24/12, or 25/05 XML BoM format, and they
support reading and writing these files.

The :class:`~ansys.grantami.bomanalytics.bom_types.eco2505.BillOfMaterials` represents the root object in a 25/05 BoM
hierarchy and can be used to programmatically generate a BoM.

Builders are available to help with creation of Granta MI reference objects. These assist in ensuring valid combinations
of identifiers. For more information, see :ref:`ref_grantami_bomanalytics_bom_builders`.

Serialization and deserialization of BoM objects can be performed using the
:class:`~ansys.grantami.bomanalytics._bom_helper.BoMHandler` class. This class exposes methods to read a BoM from a
string or a file and to write to a string or a file. The resulting BoM can be passed to either a Sustainability or a
Compliance query.

.. versionadded:: 2.0

.. toctree::
   :maxdepth: 1

   eco2505
   eco2412
   eco2301
   builders
   gbt1205
   helpers
   schemas
