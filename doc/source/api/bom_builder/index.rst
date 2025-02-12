.. _ref_grantami_bomanalytics_bom_helpers_index:

BoM helpers
==============

This section provides an introduction to the BoM helpers. These represent a BoM (bill of materials) in Ansys Granta
MI 2301 XML BoM format, and they support reading and writing these files.

The :class:`~ansys.grantami.bomanalytics.bom_types.eco2301._bom_types.BillOfMaterials` represents the root object in a BoM hierarchy and can
be used to programmatically generate a BoM.

To aid in manipulation of these objects, builders have been provided for Granta MI object references. These assist in
the correct formation of these reference objects, depending on how you need to refer to these entities.

Serialization and deserialization of BoM objects can be performed using the :class:`~ansys.grantami.bomanalytics._bom_helper.BoMHandler`
class. This class exposes methods to read a BoM from a string or a file and to write to a string or a file. The resulting BoM can be
passed to either a Sustainability or a Compliance query.

.. versionadded:: 2.0

.. toctree::
   :maxdepth: 2

   api
   builders
   helpers
   schemas

