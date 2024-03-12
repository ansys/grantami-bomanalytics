import pathlib

from .examples import BOM_PART_RECORD_HISTORY_IDENTITY, examples_as_dicts, examples_as_strings

repository_root = pathlib.Path(__file__).parents[2]
inputs_dir = pathlib.Path(__file__).parent

_sample_bom_1711_path = inputs_dir / "bom.xml"
with open(_sample_bom_1711_path, "r") as f:
    sample_bom_1711 = f.read()

_sample_compliance_bom_1711_path = (
    repository_root / "examples" / "3_Advanced_Topics" / "supporting-files" / "bom-complex.xml"
)
with open(_sample_compliance_bom_1711_path, "r") as f:
    sample_compliance_bom_1711 = f.read()

sample_bom_custom_db = sample_compliance_bom_1711.replace(
    "MI_Restricted_Substances", "MI_Restricted_Substances_Custom_Tables"
)

_sample_sustainability_bom_2301_path = (
    repository_root / "examples" / "4_Sustainability" / "supporting-files" / "bom-2301-assembly.xml"
)
with open(_sample_sustainability_bom_2301_path, "r") as f:
    sample_sustainability_bom_2301 = f.read()

_large_bom_2301_path = inputs_dir / "medium-test-bom.xml"
with open(_large_bom_2301_path, "r") as f:
    large_bom_2301 = f.read()
