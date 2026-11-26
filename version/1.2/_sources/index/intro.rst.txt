Introduction
------------
This project is part of the larger PyAnsys effort to facilitate the use
of Ansys technologies directly from within Python.

Granta MI provides a mature and feature-rich method for managing
compliance data as part of the Restricted Substances solution.
When combined with the Granta MI BoM Analyzer and Restricted Substances
Reports, the data managed in Granta MI can be leveraged to
determine compliance for complex specification hierarchies, assemblies,
and even entire products.

The ``grantami-bomanalytics`` package takes the functionality available
interactively through the web Granta MI browser and exposes it as an API.
The expected use cases for this package are as follows:

- Rolling up compliance results periodically and storing these results
  in Granta MI.
- Scripting compliance calculations as part of a release process.
- Allowing compliance to be determined for BoMs (Bills of Materials) stored
  in third-party systems, such as PLM or ERP systems.


Background
----------
The Granta MI Restricted Substances solution includes a REST API for
evaluating compliance of products, assemblies, specifications, and
materials against legislations. This package automatically abstracts
generated code into an easy-to-use client library.


Dependencies
------------
To use the ``grantami-bomanalytics`` package, you must have access
to a Granta MI server that includes MI Restricted Substances Reports
2022 R1 or later. This package also has the following Python package
dependencies:

- ``ansys-grantami-bomanalytics-openapi`` package
- ``ansys-openapi-common`` package

These package dependencies are installed automatically by
`pip <https://github.com/pypa/pip>`_, the package installer for
Python. For more information, see the installation information
in :ref:`ref_getting_started_grantami_bomanalytics`.
