# Changelog

## grantami-bomanalytics 2.1.0, TBD

### New features

* [Issue #454](https://github.com/ansys/grantami-bomanalytics/issues/454),
  [Pull request #465](https://github.com/ansys/grantami-bomanalytics/pull/465): Add `percentage_amount` to `SubstanceWithComplianceResult`.

### Doc improvements

* [Issue #466](https://github.com/ansys/grantami-bomanalytics/issues/466),
  [Pull request #467](https://github.com/ansys/grantami-bomanalytics/pull/467): Tidy up bulleted lists in API documentation.

### Contributors

* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)

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
