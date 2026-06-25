.. _ref_grantami_bomanalytics_batching:

Batching requests
=================

Queries performed with this package are batched if they exceed a certain size. When
you perform a query, batching is achieved by splitting the list of parts and materials
into smaller lists to reduce the overall time it takes to obtain results.

The exact optimal size for batching cannot be determined generally because it depends
on the data that is used to determine impacted substances and compliance. Given the
following conditions, you might need to change the batch size.

Very complex part and specification hierarchies
-----------------------------------------------
Parts and specifications in Granta MI can be defined recursively. For example, it's possible
to define parts and specifications in terms of other parts and specifications. To take this
into consideration, the default batch size for parts and specifications is very small. However,
for a very complex hierarchy, you might need to further decrease the batch size.

Very simple part and specification hierarchies
----------------------------------------------
Part and specification structures are very simple if they have a similar complexity to materials.
For example, a very simple hierarchy might directly reference substances or reference a small number
of materials. For a very simple hierarchy, you might need to increase the batch size.

Large numbers of indicators or legislations
-------------------------------------------
Queries can only be batched in the ``item`` dimension. There is no facility to split the query
by the number of legislations or indicators. As a result, if queries for impacted substances or
compliance are evaluated against a large number of legislations or lists (typically greater than
10), you might need to decrease the batch size.
