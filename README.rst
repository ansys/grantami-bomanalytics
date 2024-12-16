|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black| |pre-commit-ci|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?labelColor=black&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-grantami-bomanalytics?logo=pypi
   :target: https://pypi.org/project/ansys-grantami-bomanalytics/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-grantami-bomanalytics.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-grantami-bomanalytics
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/grantami-bomanalytics/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/grantami-bomanalytics
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/grantami-bomanalytics/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/grantami-bomanalytics/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit-ci| image:: https://results.pre-commit.ci/badge/github/ansys/grantami-bomanalytics/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/grantami-bomanalytics/main
   :alt: pre-commit.ci status


ansys-grantami-bomanalytics
###########################

Project Overview
----------------
PyGranta BoM Analytics is part of the larger `PyAnsys <https://docs.pyansys.com>`_
effort to facilitate the use of Ansys technologies directly from Python.

The MI Restricted Substances and MI Sustainability solutions for Granta MI include REST APIs for:

 - Evaluating compliance of products, assemblies, specifications, and
   materials against legislations.
 - Evaluating the environmental performance of products, assemblies, materials and processes.

This package abstracts automatically-generated code into an easy-to-use client library.


Dependencies
------------
.. readme_software_requirements

To use the ``grantami-bomanalytics`` package, you must have access to a Granta MI server that
includes MI Restricted Substances and Sustainability Reports 2024 R2 or later.

``MI Restricted Substances`` and ``MI Sustainability`` are licensed separately.
Endpoints available to end users depend on the available licenses.

The ``ansys.grantami.bomanalytics`` package currently supports Python version 3.9 through 3.12.

.. readme_software_requirements_end


Installation
------------
.. readme_installation

To install the latest PyGranta BoM Analytics release from
`PyPI <https://pypi.org/project/ansys-grantami-bomanalytics/>`_, run this command:

.. code::

   pip install ansys-grantami-bomanalytics

To install a release compatible with a specific version of Granta MI Restricted Substances and Sustainability Reports,
install the `PyGranta <https://grantami.docs.pyansys.com/>`_ metapackage with a requirement specifier:

.. code::

    pip install pygranta==2023.2.0

To see which individual PyGranta package versions are installed with each version of the PyGranta metapackage, consult
the `Package versions <https://grantami.docs.pyansys.com/version/dev/package_versions.html>`_ section of the PyGranta
documentation.

Alternatively, to install the latest development version from the
`PyGranta BoM Analytics repository <https://github.com/ansys/grantami-bomanalytics>`_, run this command:

.. code::

   git clone https://github.com/ansys/grantami-bomanalytics
   cd grantami-bomanalytics
   pip install .


Documentation
-------------
The `PyGranta BoM Analytics Documentation <https://bomanalytics.grantami.docs.pyansys.com>`_
provides comprehensive installation and usage information.


Usage
-----
Here's a brief example of how to use PyGranta BoM Analytics:

.. code:: python

    # Connect and query the Granta service.

    >>> from pprint import pprint
    >>> from ansys.grantami.bomanalytics import Connection, queries
    >>> cxn = Connection("http://my_grantami_server/mi_servicelayer").with_autologon().connect()
    >>> query = (
    ...     queries.MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['plastic-abs-pvc-flame'])
    ...     .with_legislation_ids(['Candidate_AnnexXV'])
    ... )

    # Print out the result from the query.

    >>> result = cxn.run(query)
    >>> pprint(result.impacted_substances)
    [<ImpactedSubstance: {"cas_number": 10108-64-2, "percent_amount": 1.9}>,
     <ImpactedSubstance: {"cas_number": 107-06-2, "percent_amount": None}>,
     <ImpactedSubstance: {"cas_number": 115-96-8, "percent_amount": 15.0}>,
    ...


Testing
-------
For information on testing, see the ``Contributing`` section of the documentation.


License
-------
PyGranta BoM Analytics is provided under the terms of the MIT license. You can find
this license in the LICENSE file at the root of the repository.
