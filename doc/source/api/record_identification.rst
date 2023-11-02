.. _ref_grantami_bomanalytics_record_identification:

Record identification
=====================


BoM queries
-----------

Returned input BoM items
~~~~~~~~~~~~~~~~~~~~~~~~~

BoM queries accept a BoM as input to the request. According to the Ansys Granta MI XML BoM formats,
record references can be defined in many ways. As a general rule, items in the query result which correspond to an
item provided in the input BoM, are described by the same identifier.

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

then the objects in the response are identified by ``record_guid``, unless the attribute used for the lookup is a
special identifier such as:

- ``part_number``
- ``material_id``
- ``cas_number``
- ``specification_id``

in which case the corresponding property is populated.


Expanded BoM items
~~~~~~~~~~~~~~~~~~

Expanded items are items that were not included in the input BoM, but were expanded during the analysis from other
items included in the input BoM. For example, specifications in a
:class:`~ansys.grantami.bomanalytics.queries.BomComplianceQuery` are expanded, and the linked specifications are
included in the analysis.

Expanded items are identified by the ``record_history_identity`` property.


Item queries
------------
 .. py:currentmodule:: ansys.grantami.bomanalytics.queries

Returned request items
~~~~~~~~~~~~~~~~~~~~~~

Queries that accept record references as inputs, such as :class:`~PartComplianceQuery`, allow the input records to be
defined via different identifiers.

The corresponding item in the query result is identified by the same identifier than the one used in the request.

For example, parts added to the query with :meth:`~.PartComplianceQuery.with_part_numbers` are identified in the
query result by their ``part_number`` property, and parts added with :meth:`~.PartComplianceQuery.with_record_guids`
are identified in the query result by their ``record_guid`` property.

Expanded items
~~~~~~~~~~~~~~

Item queries expand children based on the links defined in MI records. For example, during the processing of a
:class:`~.PartComplianceQuery`, children parts of the requested MI Part records are expanded.

Expanded items are identified by the ``record_history_identity`` property.
