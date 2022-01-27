Introduction and Purpose
------------------------

This project is part of the larger PyAnsys effort to facilitate the use
of Ansys technologies directly from within Python.

Granta MI provides a mature and feature-rich method for managing
compliance data as part of the Restricted Substances solution.
When combined with the Granta MI BoM Analyzer and Restricted Substances
Reports, the data managed in Granta MI can be leveraged to
determine compliance for complex specification hierarchies, assemblies,
and even entire products.

This package takes the functionality available interactively through
the web browser and exposes it as an API. The expected use cases
for this package are as follows:

- Periodically rolling up compliance results and storing the results
  in Granta MI
- Scripting compliance calculations as part of a release process
- Allowing compliance to be determined for BoMs stored in third-party
  systems, such as PLM or ERP systems
