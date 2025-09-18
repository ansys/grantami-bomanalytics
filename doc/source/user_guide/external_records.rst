.. _ref_grantami_bomanalytics_external_record_references:

Using external records in analysis
==================================

.. versionadded:: 2.4

Introduction
------------

MI Restricted Substances and Sustainability Reports 2026 R1 introduces the ability to perform analysis on records stored
in separate databases to the Restricted Substances and Sustainability database. These records are referred to below as
'external records', and the databases they are stored in are referred to as 'external databases'.

Separating data across databases in this way can simplify data management by making it easier to share responsibility
and ownership for different datasets across functional groups. Additionally, it is easier to adopt the Restricted
Substances and Sustainability solution if existing data can be easily linked to representative data supplied with the
Restricted Substances and Sustainability database.

When a BoM Analytics query is submitted that includes external records, Granta MI first identifies equivalent Restricted
Substances and Sustainability records by following cross-database links between the Restricted Substances and
Sustainability records and the external records. The results include both the Restricted Substances and Sustainability
records and the external records, providing clear traceability for how the results were determined.

This page describes the pre-requisites for performing analysis based on external records, and provides code examples for
common use cases.

.. _ref_grantami_bomanalytics_external_record_references_pre_reqs:


Pre-requisites
--------------

The following conditions must be met to use this feature:

* The version of this package must be version 2.4 or later.
* The Granta MI server is running MI Restricted Substances and Sustainability Reports 2026 R1 or later.
* The records used for analysis are linked to equivalent records in the main Restricted Substances and Sustainability
  database. See the Granta MI Restricted Substances and Sustainability Install and Configuration, on the Ansys Help
  Center for more details.


Record-based queries
--------------------

For record-based queries, the ``database_key`` argument should be used when referring to external records. For example,
a material impacted substances analysis can be performed on external material records in the
``MI_Mechanical_Design_Data`` database with the following query:

.. code-block:: python

   query = (
       MaterialImpactedSubstancesQuery()
       .with_material_ids(
           material_ids=["AB-01", "BC-02", "CD-03"],
           external_database_key="MI_Mechanical_Design_Data",
       )
       .with_legislation_ids("SINList", "CCC")
   )

If the :ref:`ref_grantami_bomanalytics_external_record_references_pre_reqs` are met, the results include
:class:`.MaterialWithImpactedSubstancesResult` objects with the following properties set:

* The :attr:`~.MaterialWithImpactedSubstancesResult.record_guid` property is set to the record GUID of the linked
  material record in the Restricted Substances and Sustainability database.
* The :attr:`~.MaterialWithImpactedSubstancesResult.database_key` property is ``None``.
* The :attr:`~.MaterialWithImpactedSubstancesResult.equivalent_references` property is a list containing a single
  :class:`.MaterialReference` object.

The 'equivalent' :class:`.MaterialReference` object would have the following properties set:

* The :attr:`~.MaterialReference.material_id` property is would be set to the appropriate material ID, for example
  "AB-01" for the first material record in the example.
* The :attr:`~.MaterialReference.database_key` property is ``MI_Mechanical_Design_Data``.
* The :attr:`~.MaterialReference.equivalent_references` property is ``None``.


BoM-based queries
-----------------

 .. py:currentmodule:: ansys.grantami.bomanalytics.bom_types

For BoM-based queries, the external database key should be used in the record or attribute reference, typically when
using the :class:`~.RecordReferenceBuilder` or :class:`~.AttributeReferenceBuilder` classes. For example, sustainability
analysis can be performed on a BoM which contains the following material reference:

.. code-block:: xml

   <MIMaterialReference>
     <dbKey>MI_Mechanical_Design_Data</dbKey>
     <recordGUID>2086f56a-4f4d-4850-9891-3d6ad155d1f9</recordGUID>
   </MIMaterialReference>

Assuming the :ref:`ref_grantami_bomanalytics_external_record_references_pre_reqs` are met, the results include a
corresponding :class:`.MaterialWithSustainabilityResult` object with the following properties set:

* The :attr:`~.MaterialWithSustainabilityResult.record_guid` property is set to the record GUID of the linked material
  record in the Restricted Substances and Sustainability database.
* The :attr:`~.MaterialWithSustainabilityResult.database_key` property is ``None``.
* The :attr:`~.MaterialWithSustainabilityResult.equivalent_references` property is a list containing a single
  :class:`.MaterialReference` object.

The 'equivalent' :class:`.MaterialReference` object would have the following properties set:

* The :attr:`~.MaterialReference.record_guid` property is ``2086f56a-4f4d-4850-9891-3d6ad155d1f9``.
* The :attr:`~.MaterialReference.database_key` property is ``MI_Mechanical_Design_Data``.
* The :attr:`~.MaterialReference.equivalent_references` property is ``None``.
