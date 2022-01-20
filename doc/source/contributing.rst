.. _contributing:

============
Contributing
============
We welcome any code contributions, and we hope that this
guide will facilitate an understanding of the Granta MI BoM
Analytics code repository. It is important to note that while the
BoM Analytics software package is maintained by Ansys and any
submissions will be reviewed thoroughly before merging, we still
seek to foster a community that can support user questions and
develop new features to make this software a useful tool for all
users. As such, we welcome and encourage any questions or
submissions to this repository.


Cloning the Source Repository
-----------------------------

You can clone the source repository from `BoM Analytics
GitHub <https://github.com/pyansys/grantami-bomanalytics>`_
and install the latest version in development mode by running:

.. code::

    git clone https://github.com/pyansys/grantami-bomanalytics
    cd grantami-bomanalytics
    pip install -e .


Questions
---------
For general or technical questions about the project, its
applications, or about software usage, please create an issue at
`BoM Analytics Issues <https://github.com/pyansys/grantami-bomanalytics/issues>`_
where the community or PyAnsys developers can collectively address your
questions.  The project support team can be reached at
`andrew.grigg@ansys.com <andrew.grigg@ansys.com>`_

By posting on the issues page, your question can be addressed by
community members with the needed expertise and the knowledge gained
will remain available on the issues page for other users.


Reporting Bugs
--------------
If you encounter any bugs or crashes while using Granta MI BoM
Analytics, please report it at
`BoM Analytics Issues <https://github.com/pyansys/grantami-bomanalytics/issues>`_
with an appropriate label so we can promptly address it.  When
reporting an issue, please be overly descriptive so that we may
reproduce it. Whenever possible, please provide tracebacks,
screenshots, and sample files to help us address the issue.


Feature Requests
----------------
We encourage users to submit ideas for improvements to Granta MI BoM Analytics!
To suggest an improvement, create an issue on the
`BoM Analytics Issues <https://github.com/pyansys/grantami-bomanalytics/issues>`_
page with a **Feature Request** label.
Please use a descriptive title and provide ample background information to help
the community implement that functionality. For example, if you would like a
reader for a specific file format, please provide a link to documentation of
that file format and possibly provide some sample files with screenshots to work
with. We will use the issue thread as a place to discuss and provide feedback.


Contributing New Code
---------------------
If you have an idea for how to improve Granta MI BoM Analytics,
consider first creating an issue as a feature request which we can use as a
discussion thread to work through how to implement the contribution.

Once you are ready to start coding, please see the `Development
Practices <#development-practices>`__ section for more details.


Licensing
---------
All contributed code will be licensed under The MIT License found in
the repository. If you did not write the code yourself, it is your
responsibility to ensure that the existing license is compatible and
included in the contributed files or you can obtain permission from
the original author to relicense the code.

--------------

Development Practices
---------------------
This section provides a guide to how we conduct development in the
Granta MI BoM Analytics repository. Please follow the practices
outlined here when contributing directly to this repository.

Guidelines
~~~~~~~~~~

Consider the following general coding paradigms when contributing:

1. Follow the `Zen of Python <https://www.python.org/dev/peps/pep-0020/>`__. As
   silly as the core Python developers are sometimes, there's much to
   be gained by following the basic guidelines listed in PEP 20.
   Without repeating them here, focus on making your additions
   intuitive, novel, and helpful for Granta MI BoM Analytics and its users.

   When in doubt, ``import this``

2. **Document it**. Include a docstring for any function, method, or
   class added.  Follow the `numpydocs docstring
   <https://numpydoc.readthedocs.io/en/latest/format.html>`_
   guidelines, and always provide an example of simple use cases for
   the new features.

3. **Test it**. Since Python is an interpreted language, if it's not
   tested, it's probably broken.  At the minimum, include unit tests
   for each new feature within the ``tests`` directory.  Ensure that
   each new method, class, or function has reasonable (>90%) coverage.

Additionally, please do not include any data sets for which a license
is not available or commercial use is prohibited.


Contributing to Granta MI BoM Analytics through GitHub
------------------------------------------------------
To submit new code to Granta MI BoM Analytics, first fork the
`Granta MI BoM Analytics repository
<https://github.com/pyansys/grantami-bomanalytics>`_ and then clone
the forked repository to your computer.  Next, create a new branch based on the
`Branch Naming Conventions Section <#branch-naming-conventions>`__ in
your local repository.

Next, add your new feature and commit it locally. Be sure to commit
often as it is often helpful to revert to past commits, especially if
your change is complex. Also, be sure to test often. See the `Testing
Section <#testing>`__ below for automating testing.

When you are ready to submit your code, create a pull request by
following the steps in the `Creating a New Pull Request
section <#creating-a-new-pull-request>`__.


Opening Issues
~~~~~~~~~~~~~~
Should you come across a bug in ``ansys-grantami-bomanalytics`` or otherwise
encounter some unexpected behaviour you should create an "issue" regarding it.
Issues are created and submitted 
`here <https://github.com/pyansys/grantami-bomanalytics/issues>`_.
Issues are used when developing to keep track of what is being
worked on at any one time, and by who. We have two issue templates
that we recommend you use:

* Bug report template
* Feature request template

If your issue does not fit into these two categories you are free
to create your own issue as well.

Issues should contain sufficient context for others to reproduce your
problem, such as the application versions you are using as well as
reproduction steps. Use issue labels like "Documentation" to further
highlight your issue's category.

Developers will respond to your issue and hopefully resolve it! Users
are encouraged to close their own issues once they are completed.
Otherwise, issues will be closed after a period of inactivity at the
discretion of the maintainers.

Should it turn out the fix did not work, or your issue was closed
erroneously, please re-open your issue with a comment addressing why.

Open ended questions should be opened in
`Discussions <https://github.com/pyansys/grantami-bomanalytics/discussions>`_,
and should an issue generate additional discussion, further issues
should be spun out into their own separate issues. This helps developers
keep track of what is being done and what needs to be done.


Discussions
~~~~~~~~~~~

General questions about Granta MI BoM Analytics should be raised in
`Discussions <https://github.com/pyansys/grantami-bomanalytics/discussions>`_
in this repository rather than as issues themselves. Issues can be spun
out of discussions depending on what is decided, but general Q&A content
should start as discussions where possible.

.. note::
    The discussions feature is still in beta on GitHub, so this may
    change in the future.


Creating a New Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once you have tested your branch locally, create a pull request on
`Granta MI BoM Analytics <https://github.com/pyansys/grantami-bomanalytics>`_
and target your merge to `main`.  This will automatically run continuous
integration (CI) testing and verify your changes will work across all
supported platforms.

For code verification, someone from the Granta MI BoM Analytics development
team will review your code to verify your code meets our standards.
Once approved, if you have write permission you may merge the branch.
If you don't have write permission, the reviewer or someone else with
write permission will merge the branch and delete the PR branch.

Since it may be necessary to merge your branch with the current
release branch (see below), please do not delete your branch if it
is a ``fix/`` branch.


Branch Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~
To streamline development, we have the following requirements for
naming branches. These requirements help the core developers know what
kind of changes any given branch is introducing before looking at the
code.

-  ``fix/``: any bug fixes, patches, or experimental changes that are
   minor
-  ``feat/``: any changes that introduce a new feature or significant
   addition
-  ``junk/``: for any experimental changes that can be deleted if gone
   stale
-  ``maint/``: for general maintenance of the repository or CI routines
-  ``doc/``: for any changes only pertaining to documentation
-  ``no-ci/``: for low impact activity that should NOT trigger the CI
   routines
-  ``testing/``: improvements or changes to testing
-  ``release/``: releases (see below)


Testing
~~~~~~~
Periodically when making changes, be sure to test locally before
creating a pull request. The following tests will be executed after
any commit or pull request, so we ask that you perform the following
sequence locally to track down any new issues from your changes.
Tests can be performed using ``tox``.

.. code::

    pip install tox
    tox -e coverage .


Static Analysis
~~~~~~~~~~~~~~~
Spell checking, coding style, and type checking is validated with the
``codespell``, ``flake8``, ``black``, and ``mypy`` tools. These tools
can be executed manually, but are easily run together with standard
settings using ``tox``.

.. code::

   tox -e lint

``codespell`` is used to check spelling in the source code, tests, and
documentation. Any misspelled words will be reported.  You can add words
to be ignored to ``ignore_words.txt``.

``flake8`` and ``black`` enforce compliance with the style guidelines
defined in `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_, and will
report any non-compliance.

The tox command above runs ``black`` in a 'check' mode, which ensures the
specified files are formatted according to the ``black`` style. It is
advised to run ``black`` before pushing git commits, which will ensure
your changes are compliant with the ``black`` style.

``mypy`` is used for static type checking. Python is a dynamically typed
language, however including type hints allows those parts of the codebase
to be analysed and validated statically. This package includes type hints
throughout, which provides benefits both when developing this package and
using it as a component in other projects.


Documentation
-------------
Documentation for Granta MI BoM Analytics is generated from three sources:

- Docstrings from the classes, functions, and modules of ``ansys.grantami.bomanalytics`` using `sphinx.ext.autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_.
- Restructured text from `doc/`
- Examples from `examples/`

General usage and API descriptions should be placed within `doc/source` and
the docstrings.  Full examples should be placed in `examples`.

Examples are only built if the environment variable 'BUILD_EXAMPLES' is set to True.
Otherwise, the example build is skipped and a placeholder page is inserted into the
documentation.

Adding a New Example
~~~~~~~~~~~~~~~~~~~~

Examples are included to give more context around the core functionality
described in the API documentation. Additional examples are welcomed,
especially if they cover a key use-case of the package which has not
previously been covered.

Examples are authored using Jupyter notebooks, but are converted into
plain .py files before being checked in. As part of the doc build process
described above, the py files are converted back into Jupyter notebooks and
are executed, which populates the output cells.

This conversion between notebooks and plain python files is performed by
`nb-convert <https://nbconvert.readthedocs.io/en/latest/>`_, see the nb-convert
documentation for installation instructions.


Documentation Style and Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Docstrings should follow the `numpydocs docstring
<https://numpydoc.readthedocs.io/en/latest/format.html>`_ guidelines.
Documentation from `doc` use reStructuredText format.  Examples
within the `examples/` directory should be PEP8 compliant and will be
compiled dynamically during the build process; ensure they run
properly locally as they will be verified through the continuous
integration performed on GitHub Actions.


Building the Documentation Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Documentation for Granta MI BoM Analytics is hosted at
`<http://grantami-bomanalytics.pyansys.com>`_ and is automatically built
and deployed using the GitHub Actions.  You can build and verify the
html documentation locally by install ``sphinx`` and the other
documentation build dependencies by running the following from the
Granta MI BoM Analytics source directory:

First, optionally install ``bomanalytics`` in development mode with:

.. code::

   pip install -e .

Then install the build requirements for documentation with:

.. code::

   pip install -r requirements_docs.txt


Next, if running Linux/Mac OS, build the documentation with:

.. code::

    make -C doc html

Otherwise, if running Windows, build the documentation by running:

.. code::

   cd doc
   make.bat html

Upon the successful build of the documentation, you can open the local
build by opening ``index.html`` at ``doc/build/html/`` with
your browser.


Continuous Integration and Continuous Delivery
----------------------------------------------
The Granta MI BoM Analytics project uses continuous integration
and delivery (CI/CD) to automate the building, testing, and
deployment tasks.  The CI Pipeline is deployed on both GitHub
Actions and Azure Pipelines and performs following tasks:

- Module wheel build
- Core API testing
- Spelling and style verification
- Documentation build


Branching Model
~~~~~~~~~~~~~~~
This project has a branching model that enables rapid development of
features without sacrificing stability, and closely follows the 
`Trunk Based Development <https://trunkbaseddevelopment.com/>`_ approach.

The main features of our branching model are:

- The `main` branch is the main development branch.  All features,
  patches, and other branches should be merged here.  While all PRs
  should pass all applicable CI checks, this branch may be
  functionally unstable as changes might have introduced unintended
  side-effects or bugs that were not caught through unit testing.
- There will be one or many `release/` branches based on minor
  releases (for example `release/0.2`) which contain a stable version
  of the code base that is also reflected on PyPi/.  Hotfixes from
  `fix/` branches should be merged both to main and to these
  branches.  When necessary to create a new patch release these
  release branches will have their `__version__.py` updated and be
  tagged with a patched semantic version (e.g. `0.2.1`).  This
  triggers CI to push to PyPi, and allow us to rapidly push hotfixes
  for past versions of ``ansys.grantami.bomanalytics`` without having
  to worry about untested features.
- When a minor release candidate is ready, a new `release` branch will
  be created from `main` with the next incremented minor version
  (e.g. `release/0.2`), which will be thoroughly tested.  When deemed
  stable, the release branch will be tagged with the version (`0.2.0`
  in this case), and if necessary merged with main if any changes
  were pushed to it.  Feature development then continues on `main`
  and any hotfixes will now be merged with this release.  Older
  release branches should not be deleted so they can be patched as
  needed.


Minor Release Steps
~~~~~~~~~~~~~~~~~~~
Minor releases are feature and bug releases that improve the
functionality and stability of ``ansys-grantami-bomanalytics``.
Before a minor release is created the following will occur:

1.  Create a new branch from the ``main`` branch with name
    ``release/MAJOR.MINOR`` (e.g. `release/0.2`).

2. Locally run all tests as outlined in the `Testing Section <#testing>`__
and ensure all are passing.

3. Locally test and build the documentation with link checking to make sure
no links are outdated. Be sure to run `make clean` to ensure no results are
cached.

    .. code::

        cd doc
        make clean  # deletes the sphinx-gallery cache
        make html -b linkcheck

4. After building the documentation, open the local build and examine
   the examples gallery for any obvious issues.

5. Update the version numbers in ``ansys/grantami/bomanalytics/_version.py``
   and commit it. Push the branch to GitHub and create a new PR for this
   release that merges it to main.  Development to main should be limited at
   this point while effort is focused on the release.

6. It is now the responsibility of the PyAnsys community and
   developers to functionally test the new release.  It is best to
   locally install this branch and use it in production.  Any bugs
   identified should have their hotfixes pushed to this release
   branch.

7. When the branch is deemed as stable for public release, the PR will
   be merged to main and the `main` branch will be tagged with a
   `MAJOR.MINOR.0` release.  The release branch will not be deleted.
   Tag the release with:

    .. code::

	git tag <MAJOR.MINOR.0>
        git push origin --tags


8. Create a list of all changes for the release. It is often helpful
   to leverage `GitHub's compare feature
   <https://github.com/pyansys/grantami-bomanalytics/compare>`_
   to see the differences from the last tag and the `main` branch.
   Be sure to acknowledge new contributors by their GitHub username
   and place mentions where appropriate if a specific contributor is
   to thank for a new feature.

9. Place your release notes from step 8 in the description within
   `BoM Analytics Releases <https://github.com/pyansys/grantami-bomanalytics/releases/new>`_


Patch Release Steps
~~~~~~~~~~~~~~~~~~~
Patch releases are for critical and important bugfixes that can not or
should not wait until a minor release.  The steps for a patch release

1. Push the necessary bugfix(es) to the applicable release branch.
   This will generally be the latest release branch
   (e.g. `release/0.2`).

2. Update `__version__.py` with the next patch increment
   (e.g. `0.2.1`), commit it, and open a PR that merge with the
   release branch.  This gives the PyAnsys developers and community
   a chance to validate and approve the bugfix release.  Any
   additional hotfixes should be outside of this PR.

3. When approved, merge with the release branch, but not `main` as
   there is no reason to increment the version of the `main` branch.
   Then create a tag from the release branch with the applicable
   version number (see above for the correct steps).

4. If deemed necessary a release notes page.
