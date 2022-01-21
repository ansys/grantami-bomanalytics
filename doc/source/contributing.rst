.. _contributing_grantami_bomanalytics:

============
Contributing
============
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/overview/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all `Guidelines and Best Practices <https://dev.docs.pyansys.com/guidelines/index.html>`_
before attempting to contribute to the ``grantami-bomanalytics`` repository.

The following contribution information is specific to the ``grantami-bomanalytics``
repository, which is for the Granta MI BoM Analytics library. This PyAnsys library name
is often used in place of the repository name to provide clarity and improve
readability.

Cloning the Source Repository
-----------------------------
Run this code to clone and install the latest version of the ``grantami-bomanalytics``
repository:

.. code::

    git clone https://github.com/pyansys/grantami-bomanalytics
    cd grantami-bomanalytics
    pip install .


Posting Issues
--------------
Use the `Issues <https://github.com/pyansys/grantami-bomanalytics/issues>`_ page for
this repository to submit questions, report bugs, and request new features.

To reach the project support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Viewing Granta MI BoM Analytics Documentation
---------------------------------------------
Documentation for the latest stable release of Granta MI BoM Analytics
is hosted at `Granta MI BoM Analytics Documentation <https://grantami.docs.pyansys.com>`_.

Examples
--------
Examples are included to give more context around the core functionality
described in the API documentation. Additional examples are welcomed,
especially if they cover a key use-case of the package which has not
previously been covered.

The example scripts are placed in the ``examples`` directory, and are included
in the documentation build if the environment variable ``BUILD_EXAMPLES`` is set
to ``True``. Otherwise, the example build is skipped and a placeholder page is
inserted into the documentation.

Examples are authored using Jupyter notebooks, but are converted into
plain .py files before being checked in. As part of the doc build process
described above, the py files are converted back into Jupyter notebooks and
are executed, which populates the output cells.

This conversion between notebooks and plain python files is performed by
`nb-convert <https://nbconvert.readthedocs.io/en/latest/>`_, see the nb-convert
documentation for installation instructions.
