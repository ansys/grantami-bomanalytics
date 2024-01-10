.. _ref_grantami_bomanalytics_query_type_differences:

Differences between BoM-based queries and record-based queries
==============================================================

.. include:: ../reusable_text/query_types.rst

This page describes the differences in how BoM-based queries and record-based queries
include additional linked items in restricted substances analyses. It also describes the ways
records are identified in the queries and responses for the different query types.

.. _ref_grantami_bomanalytics_bom_query_restrictions:

Items added during restricted substances analysis
-------------------------------------------------
In both record and BoM-based restricted substances queries, additional items are included both in
the analysis and the response based on record-to-record links in Granta MI. However, the items added
depends on the type of query used.

In the sections below, the following structure is used as an example:

* A part record, which links to...

  * A part record which contains a substance declaration,...
  * A material record which contains a substance declaration, and...
  * A specification record, which links to...

    * A specification record which contains a substance declaration.

In both cases, all items added during the analysis are always identified by the
``record_history_identity`` property in the response.

Record-based queries
~~~~~~~~~~~~~~~~~~~~
In a record-based query all children of all items included in the query are included in the analysis
and returned in the response. Considering a :class:`~.PartComplianceQuery` containing the root part
in structure described above, the child part, all child specifications, and all substances will be
included in the analysis and returned in the response.

BoM-based queries
~~~~~~~~~~~~~~~~~
In a BoM-based query, only child specifications are included in the analysis and returned in the
response. Considering a :class:`~.BoMComplianceQuery` containing the root part
in structure described above, only the child specifications are included in the analysis and
returned in the response. The child part and material are *not* included unless they are explicitly
added to the BoM.

 .. note::
  The API assumes that, excluding specifications, a BoM represents the entire structure of the
  product. The API will not use any record-to-record links in Granta MI in the analysis, except for
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
input records to be defined via different record identifiers.

The corresponding item in the query result is identified by the same identifier as the one used in
the request.

For example, parts added to the query with :meth:`~.PartComplianceQuery.with_part_numbers` are
identified in the query result by their ``part_number`` property, and parts added with
:meth:`~.PartComplianceQuery.with_record_guids` are identified in the query result by their
``record_guid`` property.

BoM-based queries
~~~~~~~~~~~~~~~~~
BoM-based queries accept a BoM as input to the request. According to the Ansys Granta MI XML BoM
formats, record references can be defined in many ways. As a general rule, items in the query result
which correspond to an item provided in the input BoM, are described by the same identifier.

For example, a ``MIMaterialReference`` in an input BoM using a ``recordGUID``

.. code-block:: xml

   <MIMaterialReference>
     <dbKey>MI_Restricted_Substances</dbKey>
     <recordGUID>2086f56a-4f4d-4850-9891-3d6ad155d1f9</recordGUID>
   </MIMaterialReference>

which is used in a :class:`~ansys.grantami.bomanalytics.queries.BomSustainabilityQuery`, results in a
:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithSustainabilityResult`, where only the
:attr:`~ansys.grantami.bomanalytics._item_results.MaterialWithSustainabilityResult.record_guid` is populated.

If the record reference in an input BoM is defined via a ``lookupValue``:

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

then the objects in the response are identified by ``record_guid``, unless the attribute used for
the lookup is a special identifier such as:

- ``part_number``
- ``material_id``
- ``cas_number``
- ``specification_id``

in which case the corresponding property is populated.
