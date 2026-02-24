.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

See `CHANGELOG.md <https://github.com/ansys/grantami-bomanalytics/blob/main/CHANGELOG.md>`_ for release notes for v2.2.0 and earlier.

.. vale off

.. towncrier release notes start

`2.4.0rc0 <https://github.com/ansys/grantami-bomanalytics/releases/tag/v2.4.0rc0>`_ - December 30, 2025
=======================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add a plot to test examples
          - `#816 <https://github.com/ansys/grantami-bomanalytics/pull/816>`_

        * - Add support for Eco 25/05 XML format
          - `#869 <https://github.com/ansys/grantami-bomanalytics/pull/869>`_

        * - Add database_key and equivalent_references to record reference-based objects
          - `#874 <https://github.com/ansys/grantami-bomanalytics/pull/874>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update tornado to v6.5
          - `#796 <https://github.com/ansys/grantami-bomanalytics/pull/796>`_

        * - Use defusedxml for parsing boms
          - `#843 <https://github.com/ansys/grantami-bomanalytics/pull/843>`_

        * - Upgrade plotly, add default renderer
          - `#865 <https://github.com/ansys/grantami-bomanalytics/pull/865>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Enable vulnerability and code quality scanning
          - `#834 <https://github.com/ansys/grantami-bomanalytics/pull/834>`_

        * - Update lock file
          - `#836 <https://github.com/ansys/grantami-bomanalytics/pull/836>`_

        * - Add security.md file
          - `#837 <https://github.com/ansys/grantami-bomanalytics/pull/837>`_

        * - Raise assertionerrors explicitly
          - `#844 <https://github.com/ansys/grantami-bomanalytics/pull/844>`_

        * - Chore: update changelog for v2.3.0
          - `#849 <https://github.com/ansys/grantami-bomanalytics/pull/849>`_

        * - Docs: update ``contributors.md`` with the latest contributors
          - `#854 <https://github.com/ansys/grantami-bomanalytics/pull/854>`_

        * - Chore: update changelog for v2.3.1
          - `#860 <https://github.com/ansys/grantami-bomanalytics/pull/860>`_

        * - Fully qualify all XML references in bom_types modules
          - `#868 <https://github.com/ansys/grantami-bomanalytics/pull/868>`_

        * - Re-work allowed_types module to support multiple arguments
          - `#873 <https://github.com/ansys/grantami-bomanalytics/pull/873>`_

        * - Update test database creation scripts
          - `#875 <https://github.com/ansys/grantami-bomanalytics/pull/875>`_

        * - Handle trailing slash on test server URL during test VM warmup
          - `#882 <https://github.com/ansys/grantami-bomanalytics/pull/882>`_

        * - Fix custom Locations table name
          - `#884 <https://github.com/ansys/grantami-bomanalytics/pull/884>`_

        * - Convert warnings to errors during tests
          - `#891 <https://github.com/ansys/grantami-bomanalytics/pull/891>`_

        * - Add missing dev dependencies to appropriate dependabot group
          - `#897 <https://github.com/ansys/grantami-bomanalytics/pull/897>`_

        * - Update tests and database preparation scripts for 2026 R1
          - `#913 <https://github.com/ansys/grantami-bomanalytics/pull/913>`_

        * - CHORE:   Update missing or outdated files
          - `#919 <https://github.com/ansys/grantami-bomanalytics/pull/919>`_

        * - Chore: Update missing or outdated files
          - `#930 <https://github.com/ansys/grantami-bomanalytics/pull/930>`_

        * - Fix failing integration tests after 2026 R1 update
          - `#935 <https://github.com/ansys/grantami-bomanalytics/pull/935>`_

        * - Add support for python 3.14
          - `#940 <https://github.com/ansys/grantami-bomanalytics/pull/940>`_

        * - Upgrade ansys-grantami-bomanalytics-openapi to 5.0.0 release
          - `#949 <https://github.com/ansys/grantami-bomanalytics/pull/949>`_

        * - Prepare 2.4.0rc0 release
          - `#950 <https://github.com/ansys/grantami-bomanalytics/pull/950>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump version to 2.4.0.dev0
          - `#791 <https://github.com/ansys/grantami-bomanalytics/pull/791>`_

        * - Add 2025 R2 stable test VM
          - `#792 <https://github.com/ansys/grantami-bomanalytics/pull/792>`_

        * - Fix version number on main branch
          - `#810 <https://github.com/ansys/grantami-bomanalytics/pull/810>`_


`2.3.1 <https://github.com/ansys/grantami-bomanalytics/releases/tag/v2.3.1>`_ - July 29, 2025
=============================================================================================

.. tab-set::


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog with link to stable docs
          - `#850 <https://github.com/ansys/grantami-bomanalytics/pull/850>`_

        * - Refer to the documentation on ansys help that relates to the 2025 r2 release
          - `#855 <https://github.com/ansys/grantami-bomanalytics/pull/855>`_

        * - Prepare 2.3.1 release
          - `#859 <https://github.com/ansys/grantami-bomanalytics/pull/859>`_


`2.3.0 <https://github.com/ansys/grantami-bomanalytics/releases/tag/v2.3.0>`_ - July 10, 2025
=============================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Support 24/12 Eco BoM
          - `#693 <https://github.com/ansys/grantami-bomanalytics/pull/693>`_

        * - Optionally raise exceptions if a BoM can't be fully deserialized
          - `#702 <https://github.com/ansys/grantami-bomanalytics/pull/702>`_

        * - Test on multiple servers
          - `#710 <https://github.com/ansys/grantami-bomanalytics/pull/710>`_

        * - Feat/support v2 api
          - `#713 <https://github.com/ansys/grantami-bomanalytics/pull/713>`_

        * - Add part and process-level transport information to BoM Sustainability responses
          - `#719 <https://github.com/ansys/grantami-bomanalytics/pull/719>`_

        * - Add transport groupings by part and by category to sustainability summary results
          - `#724 <https://github.com/ansys/grantami-bomanalytics/pull/724>`_

        * - Improve documentation of Enum classes
          - `#726 <https://github.com/ansys/grantami-bomanalytics/pull/726>`_

        * - Re-organize test BoMs and payloads
          - `#727 <https://github.com/ansys/grantami-bomanalytics/pull/727>`_

        * - Add ImplactedSubstance and Compliance integration tests for 24/12 BoMs
          - `#735 <https://github.com/ansys/grantami-bomanalytics/pull/735>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Mark failing tests as xfail
          - `#718 <https://github.com/ansys/grantami-bomanalytics/pull/718>`_

        * - Add reprs for new result classes
          - `#730 <https://github.com/ansys/grantami-bomanalytics/pull/730>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Migrate to BoM Analytics Services V2
          - `#714 <https://github.com/ansys/grantami-bomanalytics/pull/714>`_

        * - Update jinja2 to 3.1.6
          - `#740 <https://github.com/ansys/grantami-bomanalytics/pull/740>`_

        * - Update ansys-openapi-common to 2.2.2
          - `#741 <https://github.com/ansys/grantami-bomanalytics/pull/741>`_

        * - Update bomanalytics-openapi to 4.0.0.dev165
          - `#751 <https://github.com/ansys/grantami-bomanalytics/pull/751>`_

        * - Update bomanalytics-openapi to v4.0.0rc1
          - `#781 <https://github.com/ansys/grantami-bomanalytics/pull/781>`_

        * - Update bomanalytics-openapi to 4.0.0rc4
          - `#786 <https://github.com/ansys/grantami-bomanalytics/pull/786>`_

        * - Update bomanalytics-openapi dependency to 4.0.0 stable release
          - `#787 <https://github.com/ansys/grantami-bomanalytics/pull/787>`_

        * - Remove private PyPI references
          - `#788 <https://github.com/ansys/grantami-bomanalytics/pull/788>`_

        * - Prepare 2.3.0rc0 release
          - `#820 <https://github.com/ansys/grantami-bomanalytics/pull/820>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Prepare 2.3.0 release
          - `#848 <https://github.com/ansys/grantami-bomanalytics/pull/848>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Move bom types to submodule
          - `#703 <https://github.com/ansys/grantami-bomanalytics/pull/703>`_

        * - Pin plotly to <6 to avoid bug during documentation build
          - `#723 <https://github.com/ansys/grantami-bomanalytics/pull/723>`_

        * - Update examples to include transport results
          - `#728 <https://github.com/ansys/grantami-bomanalytics/pull/728>`_

        * - Documentation review
          - `#738 <https://github.com/ansys/grantami-bomanalytics/pull/738>`_

        * - Improve documentation for Granta MI reports bundle version support
          - `#779 <https://github.com/ansys/grantami-bomanalytics/pull/779>`_

        * - Add references to 24/12 BoM format in API documentation
          - `#780 <https://github.com/ansys/grantami-bomanalytics/pull/780>`_

        * - Include changelog in documentation
          - `#795 <https://github.com/ansys/grantami-bomanalytics/pull/795>`_

        * - Add an example of creating a BoM from Python classes directly
          - `#800 <https://github.com/ansys/grantami-bomanalytics/pull/800>`_, `#818 <https://github.com/ansys/grantami-bomanalytics/pull/818>`_

        * - Sankey diagram example
          - `#803 <https://github.com/ansys/grantami-bomanalytics/pull/803>`_

        * - Address example notebook formatting issues
          - `#805 <https://github.com/ansys/grantami-bomanalytics/pull/805>`_

        * - Re-organize examples to improve grouping and readability
          - `#817 <https://github.com/ansys/grantami-bomanalytics/pull/817>`_

        * - Add an example of creating a bom from a csv file
          - `#819 <https://github.com/ansys/grantami-bomanalytics/pull/819>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - chore: update CHANGELOG for v2.2.0
          - `#673 <https://github.com/ansys/grantami-bomanalytics/pull/673>`_

        * - Update License Date in Headers
          - `#681 <https://github.com/ansys/grantami-bomanalytics/pull/681>`_

        * - Add a call to BoM Analytics Services during VM start
          - `#706 <https://github.com/ansys/grantami-bomanalytics/pull/706>`_

        * - Warm up databases
          - `#708 <https://github.com/ansys/grantami-bomanalytics/pull/708>`_

        * - Run server_check.yml workflow for dependabot PRs
          - `#717 <https://github.com/ansys/grantami-bomanalytics/pull/717>`_

        * - Fix Dependabot Configuration for Private PyPI
          - `#742 <https://github.com/ansys/grantami-bomanalytics/pull/742>`_

        * - Allow dependabot server checks to run in parallel
          - `#748 <https://github.com/ansys/grantami-bomanalytics/pull/748>`_

        * - Move Integration Test check to top-level workflow
          - `#749 <https://github.com/ansys/grantami-bomanalytics/pull/749>`_

        * - docs: Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#754 <https://github.com/ansys/grantami-bomanalytics/pull/754>`_

        * - Update database preparation scripts
          - `#771 <https://github.com/ansys/grantami-bomanalytics/pull/771>`_

        * - Use PyPI-authored publish action
          - `#772 <https://github.com/ansys/grantami-bomanalytics/pull/772>`_

        * - Generate provenance attestations
          - `#773 <https://github.com/ansys/grantami-bomanalytics/pull/773>`_

        * - Bump version to 2.3
          - `#776 <https://github.com/ansys/grantami-bomanalytics/pull/776>`_

        * - Use git SHA to pin action version
          - `#785 <https://github.com/ansys/grantami-bomanalytics/pull/785>`_

        * - Move release branch to use release VM
          - `#790 <https://github.com/ansys/grantami-bomanalytics/pull/790>`_


.. vale on