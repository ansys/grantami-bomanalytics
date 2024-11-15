# Changelog

This project uses [towncrier](https://towncrier.readthedocs.io/) and the
changes for the upcoming release can be found in
<https://github.com/ansys/grantami-bomanalytics/tree/main/doc/changelog.d/>.

<!-- towncrier release notes start -->

## [2.2.0rc0](https://github.com/ansys/grantami-bomanalytics/releases/tag/v2.2.0rc0) - 2024-11-15


### Changed

- CI - 490 - Add changelog generation [#510](https://github.com/ansys/grantami-bomanalytics/pull/510)
- Define labels and add label sync CI [#518](https://github.com/ansys/grantami-bomanalytics/pull/518)
- Do not run changelog-fragment for dependabot-initiated PRs [#519](https://github.com/ansys/grantami-bomanalytics/pull/519)
- Update changelog [#529](https://github.com/ansys/grantami-bomanalytics/pull/529)
- Use trusted publisher [#549](https://github.com/ansys/grantami-bomanalytics/pull/549)
- Update main branch to 2.2.0dev0 [#551](https://github.com/ansys/grantami-bomanalytics/pull/551)
- Don't create changelog fragments for pre-commit updates [#587](https://github.com/ansys/grantami-bomanalytics/pull/587)


### Fixed

- Empty elements are no longer removed when deserializing a BoM file [#546](https://github.com/ansys/grantami-bomanalytics/pull/546)


### Dependencies

- Bump plotly from 5.21.0 to 5.22.0 [#511](https://github.com/ansys/grantami-bomanalytics/pull/511)
- Bump ansys-openapi-common from 2.0.0 to 2.0.2 [#520](https://github.com/ansys/grantami-bomanalytics/pull/520)
- Bump jinja2 from 3.1.3 to 3.1.4 [#521](https://github.com/ansys/grantami-bomanalytics/pull/521)
- Bump jupyterlab from 4.1.8 to 4.2.0 [#522](https://github.com/ansys/grantami-bomanalytics/pull/522)
- Bump jupytext from 1.16.1 to 1.16.2 [#523](https://github.com/ansys/grantami-bomanalytics/pull/523)
- Bump nbsphinx from 0.9.3 to 0.9.4 [#524](https://github.com/ansys/grantami-bomanalytics/pull/524)
- Bump ansys-grantami-bomanalytics-openapi from 3.0.0a1 to 3.0.0 [#527](https://github.com/ansys/grantami-bomanalytics/pull/527)
- Upgrade to grantami-bomanalytics-openapi 3.1.0rc1 [#635](https://github.com/ansys/grantami-bomanalytics/pull/635)


### Miscellaneous

- Update openapi-common reference link [#513](https://github.com/ansys/grantami-bomanalytics/pull/513)
- [pre-commit.ci] pre-commit autoupdate [#531](https://github.com/ansys/grantami-bomanalytics/pull/531), [#540](https://github.com/ansys/grantami-bomanalytics/pull/540), [#554](https://github.com/ansys/grantami-bomanalytics/pull/554), [#563](https://github.com/ansys/grantami-bomanalytics/pull/563), [#577](https://github.com/ansys/grantami-bomanalytics/pull/577)


### Documentation

- Update acceptance tests for 2025 R1 database [#607](https://github.com/ansys/grantami-bomanalytics/pull/607)
- Update repository link in pyproject.toml [#616](https://github.com/ansys/grantami-bomanalytics/pull/616)
- Fix installation example for git dependency [#619](https://github.com/ansys/grantami-bomanalytics/pull/619)
- Add link to PyGranta version compatibility documentation [#620](https://github.com/ansys/grantami-bomanalytics/pull/620)
- Add link to supported authentication schemes [#621](https://github.com/ansys/grantami-bomanalytics/pull/621)
- maint: 2025 R1 update [#630](https://github.com/ansys/grantami-bomanalytics/pull/630)
- Fix bulleted list in README [#643](https://github.com/ansys/grantami-bomanalytics/pull/643)
- Update Ansys documentation links to 2025 R1 [#649](https://github.com/ansys/grantami-bomanalytics/pull/649)


### Maintenance

- [pre-commit.ci] pre-commit autoupdate [#590](https://github.com/ansys/grantami-bomanalytics/pull/590)
- Auto-approve pre-commit-ci pull requests [#602](https://github.com/ansys/grantami-bomanalytics/pull/602)
- Configure environment for trusted publisher release [#617](https://github.com/ansys/grantami-bomanalytics/pull/617)
- Improve VM management in CI [#622](https://github.com/ansys/grantami-bomanalytics/pull/622)
- Update CONTRIBUTORS and AUTHORS to new format [#626](https://github.com/ansys/grantami-bomanalytics/pull/626)
- Prepare 2.2.0rc0 release [#652](https://github.com/ansys/grantami-bomanalytics/pull/652)

## grantami-bomanalytics 2.1.0, 2024-05-08

### New features

* [Issue #454](https://github.com/ansys/grantami-bomanalytics/issues/454),
  [Pull request #465](https://github.com/ansys/grantami-bomanalytics/pull/465): Add `percentage_amount` to `SubstanceWithComplianceResult`.

### Doc improvements

* [Issue #466](https://github.com/ansys/grantami-bomanalytics/issues/466),
  [Pull request #467](https://github.com/ansys/grantami-bomanalytics/pull/467): Tidy up bulleted lists in API documentation.
* [Issue #464](https://github.com/ansys/grantami-bomanalytics/issues/466),
  [Pull request #467](https://github.com/ansys/grantami-bomanalytics/pull/467): Add `versionadded` directives to API documentation.

### Contributors

* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)
* Doug Addy (Ansys)

## grantami-bomanalytics 2.0.0, 2024-01-17

### New features

* Add sustainability analysis support, including examples and documentation.
* Add `bom_types` subpackage.
* Add licensing check as part of connection to server.

### Backwards-incompatible changes

* Change the `legislation_names` method to `legislation_ids`.
* Remove `with_stk_records` method.

### Doc improvements

* Document use of the `pygranta` meta-package for managing compatibility between PyGranta and
  Granta MI.

### Contributors

* Doug Addy (Ansys)
* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)
* Judy Selfe (Ansys)

## grantami-bomanalytics 1.2.0, 2023-08-29

### Bugs fixed

* [Issue #277](https://github.com/ansys/grantami-bomanalytics/issues/277),
  [Pull request #242](https://github.com/ansys/grantami-bomanalytics/pull/282): 
  Don't include withdrawn records in analysis.

### New features

* [Issue #328](https://github.com/ansys/grantami-bomanalytics/issues/328),
  [Pull request #341](https://github.com/ansys/grantami-bomanalytics/pull/341):
  Add `maximum_specification_link_depth` property.
* [Pull request #334](https://github.com/ansys/grantami-bomanalytics/pull/334):
  Add scripts to automate test database creation.

### Doc improvements

* [Issue #291](https://github.com/ansys/grantami-bomanalytics/issues/291),
  [Pull request #343](https://github.com/ansys/grantami-bomanalytics/pull/343):
  Update documentation with new legislation names.

### Contributors

* Doug Addy (Ansys)
* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)
* Judy Selfe (Ansys)
