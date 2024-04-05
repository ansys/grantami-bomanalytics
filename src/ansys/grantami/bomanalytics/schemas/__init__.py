"""
Sub-package providing XML Schema Definition (XSD) files for Ansys Granta BoM formats.

XSD files can be used for validating XML files.
"""

from pathlib import Path

_schemas_dir = Path(__file__).parent

bom_schema_1711: Path = _schemas_dir / "BillOfMaterialsEco1711.xsd"
"""
Path to the Ansys Granta 17/11 BoM XML Schema definition.

.. versionadded:: 2.0
"""

bom_schema_2301: Path = _schemas_dir / "BillOfMaterialsEco2301.xsd"
"""
Path to the Ansys Granta 23/01 BoM XML Schema definition.

.. versionadded:: 2.0
"""
