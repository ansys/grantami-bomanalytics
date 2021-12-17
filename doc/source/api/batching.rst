.. _ref_grantami_bomanalytics_batching:

Batching Requests
=================

Introduction
------------
Queries performed with this package are batched if they exceed a certain size. This is achieved by
splitting the list of parts, materials, etc. into smaller lists to reduce the overall time taken
to perform the query.

The exact optimal size cannot be determined generally, since it depends on the data used to determine Impacted
Substances and Compliance. Situations where the batch size may need to be changed are
discussed below.

Very complex Part and Specification hierarchies
-----------------------------------------------
Parts and Specifications in Granta MI can be defined recursively, i.e. it's possible to define Parts and
Specifications in terms of other Parts and Specifications, and so on. Default batch sizes for Parts and
Specifications are very small to take this into consideration, but for very complex
hierarchies you may need to reduce this number further.

Very simple Part and Specification hierarchies
----------------------------------------------
If Part and Specification structures are very simple, for example if they have a similar complexity to materials (i.e. they directly
reference substances, or reference a small number of materials), then the batch size can be increased.

Large numbers of Indicators or Legislations
-------------------------------------------
Queries can only be batched in the 'item' dimension; there is no facility to split the query by the number of
legislations or indicators. As a result, if Impacted Substances or Compliance queries are evaluated against a large
number (typically > 10) of legislations or lists, you may need to reduce the batch size.
