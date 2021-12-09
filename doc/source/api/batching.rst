.. _ref_grantami_bomanalytics_batching:

Batching Requests
=================

Introduction
------------
[TECHDOCS] The queries that can be performed with this package are batched if they exceed a certain size. This is achieved by
splitting the list of parts, materials, etc. into smaller lists below a certain size to reduce the overall time taken
to perform the query.

The exact optimal size cannot be determined generally, since it depends on the data used to determine Impacted
Substances and Compliance. There are several situations where the batch size may need to be changed, these are
discussed below.

Very Complex Part and Specification Hierarchies
-----------------------------------------------
Parts and Specifications in Granta MI can be defined recursively, i.e. it's possible to define Parts and
Specifications in terms of other Parts and Specifications, and so on. The default batch sizes for Parts and
Specifications are set very small to take this into consideration, but in the extreme case of very complex
hierarchies it may be required to reduce this number.

Very Simple Part and Specification Hierarchies
----------------------------------------------
If part and spec structures are very simple, potentially with a similar complexity to materials (i.e. they directly
reference substances, or reference a small number of materials), then the batch size for these queries can be increased.

Large Numbers of Indicators and Legislations
--------------------------------------------
The queries can only be batched in the 'item' dimension; there is no facility to split the query by the number of
legislations or indicators. As a result, if the impacted substances or compliance queries are evaluated against a large
number (i.e. > 10) of legislations or lists, it will be required to reduce the batch size.
