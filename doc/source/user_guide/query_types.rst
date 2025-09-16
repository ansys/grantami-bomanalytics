.. _ref_query_types:

Differences between BoM and record queries
==========================================

The queries supported by the ``grantami-bomanalytics`` package can be split into two
broad groups: record-based queries and BoM-based queries. Whereas BoM-based queries
can only be constructed with a single BoM, record-based queries can be constructed
with any number of records. For example, a
:class:`~ansys.grantami.bomanalytics.queries.SpecificationImpactedSubstancesQuery`
instance could include any number of specification references.

This page describes the differences in how BoM-based queries and record-based queries
include additional linked items in restricted substances analyses. It also describes the ways
records are identified in the queries and responses for the different query types.

.. _ref_grantami_bomanalytics_bom_query_restrictions:

Items added during restricted substances analysis
-------------------------------------------------
In both record and BoM-based restricted substances queries, additional items are included both in
the analysis and the response based on record-to-record links in Granta MI. However, the items added
depend on the type of query used.

In subsequent sections, the following structure is used as an example:

* A part record, which links to:

  * A part record that contains a substance declaration,
  * A material record that contains a substance declaration, and
  * A specification record, which links to:

    * A specification record that contains a substance declaration.

In both query types, all items added during the analysis are always identified by the
``record_history_identity`` property in the response.

Record-based queries
~~~~~~~~~~~~~~~~~~~~
In a record-based query, all children of all items included in the query are included in the analysis
and returned in the response. Considering a :class:`~.PartComplianceQuery` instance containing the
root part in the preceding structure, the child part, all child specifications, and all substances are
included in the analysis and returned in the response.

BoM-based queries
~~~~~~~~~~~~~~~~~
In a BoM-based query, only child specifications are included in the analysis and returned in the
response. Considering a :class:`~.BomComplianceQuery` instance containing the root part
in the preceding structure, only the child specifications are included in the analysis and
returned in the response. The child part and material are *not* included unless they are explicitly
added to the BoM.

.. note::
   The API assumes that, excluding specifications, a BoM represents the entire structure of the
   product. The API does not use any record-to-record links in Granta MI in the analysis, except for
   specification records.

   If you want to use a BoM-based query, you *must* include the full product
   structure in the BoM, including substances.


.. _ref_grantami_bomanalytics_record_identification:

Record identification
---------------------

Record-based queries
~~~~~~~~~~~~~~~~~~~~
 .. py:currentmodule:: ansys.grantami.bomanalytics.queries

Queries that accept record references as inputs, such as :class:`~PartComplianceQuery`, allow the
input records to be defined with different record identifiers.

The corresponding item in the query result is identified by the same identifier as the one used in
the request.

For example, parts added to the query with the :meth:`~.PartComplianceQuery.with_part_numbers`
method are identified in the query result by their ``part_number`` property, and parts added with
the :meth:`~.PartComplianceQuery.with_record_guids` method are identified in the query result by
their ``record_guid`` property.

BoM-based queries
~~~~~~~~~~~~~~~~~
BoM-based queries accept a BoM as input to the request. According to the Ansys Granta MI XML BoM
formats, record references can be defined in many ways. As a general rule, items in the query result
that correspond to an item provided in the input BoM are described by the same identifier.

For example, assume that ``MIMaterialReference`` in an input BoM uses a ``recordGUID``,
which is used in a :class:`~ansys.grantami.bomanalytics.queries.BomSustainabilityQuery`
instance:

.. code-block:: xml

   <MIMaterialReference>
     <dbKey>MI_Restricted_Substances</dbKey>
     <recordGUID>2086f56a-4f4d-4850-9891-3d6ad155d1f9</recordGUID>
   </MIMaterialReference>

This results in a :class:`~ansys.grantami.bomanalytics._item_results.MaterialWithSustainabilityResult`
instance, where only the
:attr:`~ansys.grantami.bomanalytics._item_results.MaterialWithSustainabilityResult.record_guid` is populated.

Now assume that the record reference in an input BoM is defined with a ``lookupValue``:

.. code-block:: xml

    <MIPartReference>
        <dbKey>MI_Restricted_Substances</dbKey>
            <lookupValue>
                <attributeReference>
                    <dbKey>MI_Restricted_Substances</dbKey>
                    <name>
                        <table>
                            <tableName>Products and parts</tableName>
                        </table>
                        <attributeName>Part number</attributeName>
                    </name>
                </attributeReference>
            <attributeValue>CYLINDER</attributeValue>
        </lookupValue>
    </MIPartReference>

The objects in the response are then identified by ``record_guid``, unless the attribute used for
the lookup is a special identifier such as:

- ``part_number``
- ``material_id``
- ``cas_number``
- ``specification_id``

In such a case, the corresponding property is populated.

.. _ref_grantami_bomanalytics_external_record_references:

External record references
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 2.4

This package supports performing analysis on records stored in external databases, as long as the following conditions
are met:

* ``grantami-bomanalytics`` version 2.4 or later is used.
* The Granta MI server is running MI Restricted Substances and Sustainability Reports 2061 R1 or later.
* The records used for analysis are linked to equivalent records in the main Restricted Substances and Sustainability
  database. See Ansys help for more details.

For record-based queries, the ``database_key`` argument should be used when referring to records in an external
database, for example in the :meth:`~.PartComplianceQuery.with_record_guids` method.

 .. py:currentmodule:: ansys.grantami.bomanalytics.bom_types

For BoM-based queries, the external database key should be used in the record or attribute reference, typically when
using the :class:`~.RecordReferenceBuilder` or :class:`~.AttributeReferenceBuilder` classes.
