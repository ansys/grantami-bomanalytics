.. _contributing_grantami_bomanalytics:

==========
Contribute
==========
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to the ``grantami-bomanalytics``
repository.

The following contribution information is specific to the ``grantami-bomanalytics``
repository, which is for the Granta MI BoM Analytics library. This PyAnsys library name
is often used in place of the repository name to provide clarity and improve
readability.

Clone the source repository
---------------------------
Run the following code to clone and install the latest version of the ``grantami-bomanalytics``
repository. It installs the package in editable mode, which ensures changes to the code
are immediately visible in the environment. It also installs the required development
dependencies to run the tests.

.. code::

    git clone https://github.com/pyansys/grantami-bomanalytics
    cd grantami-bomanalytics
    poetry install


Post issues
-----------
Use the `Issues <https://github.com/pyansys/grantami-bomanalytics/issues>`_ page for
this repository to submit questions, report bugs, and request new features.

To reach the PyAnsys support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

View Granta MI BoM Analytics documentation
------------------------------------------
Documentation for the latest stable release of Granta MI BoM Analytics
is hosted at `Granta MI BoM Analytics Documentation <https://grantami.docs.pyansys.com>`_.

View examples
-------------
Examples are included in the documentation to give you more context around
the core functionality described in :ref:`ref_grantami_bomanalytics_api_index`.
Additional examples are welcomed, especially if they cover a key use case of the
package that has not yet been covered.

The example scripts are placed in the ``examples`` directory and are included
in the documentation build if the environment variable ``BUILD_EXAMPLES`` is set
to ``True``. Otherwise, the building of examples is skipped and a placeholder page is
inserted in the documentation.

Examples are authored using Jupyter notebooks, but they are converted into
Python files before being checked in. As part of the doc build process, the Python
files are converted back into Jupyter notebooks and are executed, which populates
the output cells.

This conversion between Jupyter notebooks and Python files is performed by
`nb-convert <https://nbconvert.readthedocs.io/en/latest/>`_. For installation
instructions, see the nb-convert documentation.
