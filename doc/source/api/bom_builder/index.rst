.. _ref_grantami_bomanalytics_bom_helpers_index:

BoM helpers
==============

.. versionadded:: 2.0

This section provides an introduction to the BoM Helpers. These represent a BoM (bill of materials) in Ansys Granta
MI 2301 XML BoM format, and support reading and writing these files.

The :class:`~ansys.grantami.bomanalytics.bom_types._bom_types.BillOfMaterials` represents the root object in a BoM hierarchy, and can
be used to programmatically generate a BoM.

To aid in manipulation of these objects, builders have been provided for Granta MI object references. These assist in
the correct formation of these reference objects, depending on how you need to refer to these entities.

Serialization and Deserialization of BoM objects can be performed using the :class:`~ansys.grantami.bomanalytics._bom_helper.BoMHandler`.
This exposes methods to read a BoM from a string or a file, and to write to a string or a file. The resulting BoM can be
passed to either a Sustainability or a Compliance query.

.. toctree::
   :maxdepth: 2

   api
   builders
   helpers
   schemas

