.. _ref_grantami_bomanalytics_record_identification:

Record identification
=====================

Query types
-----------

.. include:: ../reusable_text/query_types.rst

BoM-based queries
-----------------

Input BoM items included in the response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Record-based queries
--------------------
 .. py:currentmodule:: ansys.grantami.bomanalytics.queries

Returned request items
~~~~~~~~~~~~~~~~~~~~~~

Queries that accept record references as inputs, such as :class:`~PartComplianceQuery`, allow the
input records to be defined via different record identifiers.

The corresponding item in the query result is identified by the same identifier than the one used in
the request.

For example, parts added to the query with :meth:`~.PartComplianceQuery.with_part_numbers` are
identified in the query result by their ``part_number`` property, and parts added with
:meth:`~.PartComplianceQuery.with_record_guids` are identified in the query result by their
``record_guid`` property.

Items added during analysis
---------------------------

In both record and BoM-based queries, additional items are included both in the analysis and the
response based on links defined in the records in Granta MI. For example, during the processing of a
:class:`~.PartComplianceQuery`, children of the referenced part are included in the analysis and
returned in the response. Similarly, in a :class:`~.BoMComplianceQuery`, child items of any parts
and specifications included in the BoM will be included in the analysis and returned in the
response.

Items added during the analysis are always identified by the ``record_history_identity`` property.
