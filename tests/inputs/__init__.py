import pathlib

from .examples import examples_as_dicts, examples_as_strings

repository_root = pathlib.Path(__file__).parents[2]

_bom_path = pathlib.Path(__file__).parent / "bom.xml"
with open(_bom_path, "r") as f:
    sample_bom_1711 = f.read()

_complex_bom_path = repository_root / "examples" / "3_Advanced_Topics" / "supporting-files" / "bom-complex.xml"
with open(_complex_bom_path, "r") as f:
    sample_compliance_bom_1711 = f.read()

sample_bom_custom_db = sample_compliance_bom_1711.replace(
    "MI_Restricted_Substances", "MI_Restricted_Substances_Custom_Tables"
)

_bom_2301_path = repository_root / "examples" / "4_Sustainability" / "supporting-files" / "bom-2301-assembly.xml"
with open(_bom_2301_path, "r") as f:
    sample_sustainability_bom_2301 = f.read()
