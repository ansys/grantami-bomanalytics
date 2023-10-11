import pathlib

from .examples import examples_as_dicts, examples_as_strings

_bom_path = pathlib.Path(__file__).parent / "bom.xml"
with open(_bom_path, "r") as f:
    sample_bom = f.read()

_complex_bom_path = pathlib.Path(__file__).parent / "bom-complex.xml"
with open(_complex_bom_path, "r") as f:
    sample_bom_complex = f.read()

sample_bom_custom_db = sample_bom_complex.replace("MI_Restricted_Substances", "MI_Restricted_Substances_Custom_Tables")


repository_root = pathlib.Path(__file__).parent.parent.parent

_bom_2301_path = repository_root / "examples" / "4_Sustainability" / "supporting-files" / "bom-2301-assembly.xml"
with open(_bom_2301_path, "r") as f:
    sample_bom_2301 = f.read()
