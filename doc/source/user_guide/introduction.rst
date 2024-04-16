Introduction
============

Granta MI provides a mature and feature-rich method for managing
restricted substances and sustainability data as part of the Granta MI
Restricted Substances and Sustainability database. When combined with the
Granta MI BoM Analyzer and Reports, the data managed in Granta MI can be
leveraged to determine compliance and sustainability for components,
assemblies, and even entire products.

The ``grantami-bomanalytics`` package takes the functionality available
interactively through the web Granta MI browser and exposes it as an API.
The expected use cases for this package are as follows:

- Rolling up compliance and sustainability results periodically and storing
  these results in Granta MI.
- Scripting compliance and sustainability calculations as part of a release
  process.
- Allowing compliance and sustainability to be determined for BoMs (Bills of
  Materials) stored in third-party systems, such as PLM or ERP systems.

This package provides access to two similar but distinct APIs:

#. The Granta MI Restricted Substances API is used to determine the impacted
   substances and compliance of products, assemblies, specifications, and
   materials against one or more legislations.
#. The Granta MI Sustainability API is used to evaluate the environmental
   performance of products, assemblies, materials, manufacturing processes
   and transport stages.

In both cases, this package makes the underlying REST APIs easier to use by
providing idiomatic Python interfaces and example scripts.

This package also provides a sub-package to help constructing Granta XML BoMs.
