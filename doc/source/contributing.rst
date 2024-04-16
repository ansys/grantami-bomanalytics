.. _ref_contributing:

Contribute
##########

General guidelines
==================
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyGranta BoM Analytics.

The following contribution information is specific to PyGranta BoM Analytics.

Developer environment setup
===========================

PyGranta BoM Analytics uses `Poetry`_ for packaging and dependency management. Installation
information is available in the Poetry documentation.

Installing PyGranta BoM Analytics in developer mode allows you to modify and enhance
the source.

Clone the source repository
---------------------------

Run the following commands to clone and install the latest version of PyGranta BoM Analytics
in editable mode, which ensures changes to the code are immediately visible in the environment.
Running these commands also installs the required development dependencies to run the tests,
build the documentation, and build the package.

.. code:: bash

    git clone https://github.com/ansys/grantami-bomanalytics
    cd grantami-bomanalytics
    poetry install --with doc

Additional tools
-----------------

.. _ref_precommit:

Pre-commit
~~~~~~~~~~

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool with this command:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


.. _ref_tox:

Tox
~~~
Tests can be run using `tox`_. The project defines the tox environments in the ``tox.ini``
file. One tox environment is provided:

.. vale off

- ``tox -e tests``: Runs all tests and checks code coverage. (For requirements, see :ref:`ref_serveraccess`.)

.. vale on

Optionally, add the ``-- -m "not integration"`` suffix to the commands above to skip integration
tests. For example, this command only runs tests that do not require a Granta MI instance::

     tox -e tests -- -m "not integration"


.. _ref_serveraccess:

Server access
--------------

As indicated in :ref:`ref_software_requirements`, running integration tests and building the examples
requires access to a valid Granta MI instance.

External contributors may not have an instance of Granta MI at their disposal. Prior to creating a
pull request with the desired changes, they should make sure that unit tests pass (:ref:`ref_tox`),
static code validation and styling pass (:ref:`pre-commit <ref_precommit>`), and that the
documentation can be generated successfully without the examples
(:ref:`Documenting <ref_documenting>`).

Continuous Integration (CI) on GitHub is configured to run the integration tests and generate the
full documentation on creation and updates of pull requests. CI is not configured to run for pull
requests from forks. External contributions require approval from a maintainer for checks to run.

Code formatting and styling
===========================

This project adheres to PyAnsys styling and formatting recommendations. The easiest way to
validate changes are compliant is to run this command:

.. code:: bash

    pre-commit run --all-files


.. _ref_documenting:

Documenting
===========

As per PyAnsys guidelines, the documentation is generated using `Sphinx`_.

For building documentation, use the Sphinx Makefile:

.. code:: bash

    make -C doc/ html && your_browser_name doc/build/html/index.html

If any changes have been made to the documentation, you should run
Sphinx directly with the following extra arguments:

.. code:: bash

    sphinx-build -b html source build -W -n --keep-going

The extra arguments ensure that all references are valid and turn warnings
into errors. CI uses the same configuration, so you should resolve any
warnings and errors locally before pushing changes.


Example notebooks
=================
Examples are included in the documentation to give you more context around
the core capabilities described in :ref:`ref_grantami_bomanalytics_api_reference`.
Additional examples are welcomed, especially if they cover a key use case of the
package that has not yet been covered.

The example scripts are placed in the ``examples`` directory and are included
in the documentation build if the environment variable ``BUILD_EXAMPLES`` is set
to ``True``. Otherwise, a different set of examples is run to validate the process.

Examples are checked in as scripts using the ``light`` format. For more information,
see the `Jupytext documentation <jupytext_>`_. As part of the documentation-building
process, the Python files are converted back into Jupyter notebooks and the output
cells are populated by running the notebooks against a Granta MI instance.

This conversion between Jupyter notebooks and Python files is performed by
`nb-convert`_. Installation information is available in the ``nb-convert`` documentation.


Post issues
===========
Use the `PyGranta BoM Analytics Issues <https://github.com/pyansys/grantami-bomanalytics/issues>`_ page
to report bugs and request new features. When possible, use the issue templates provided. If
your issue does not fit into one of these templates, click the link for opening a blank issue.

If you have general questions about the PyAnsys ecosystem, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.
If your question is specific to PyGranta BoM Analytics, ask your question in an issue as described in
the previous paragraph.

.. _Poetry: https://python-poetry.org/
.. _pre-commit: https://pre-commit.com/
.. _tox: https://tox.wiki/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _jupytext: https://jupytext.readthedocs.io/en/latest/
.. _nb-convert: https://nbconvert.readthedocs.io/en/latest/
