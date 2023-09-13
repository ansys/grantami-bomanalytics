import pathlib
from .examples import examples_as_strings, examples_as_dicts

_bom_path = pathlib.Path(__file__).parent / "bom.xml"
with open(_bom_path, "r") as f:
    sample_bom = f.read()

_complex_bom_path = pathlib.Path(__file__).parent / "bom-complex.xml"
with open(_complex_bom_path, "r") as f:
    sample_bom_complex = f.read()

sample_bom_custom_db = sample_bom_complex.replace("MI_Restricted_Substances", "MI_Restricted_Substances_Custom_Tables")

_bom_2301_path = pathlib.Path(__file__).parent / "bom-2301.xml"
with open(_bom_2301_path, "r") as f:
    sample_bom_2301 = f.read()

_complex_bom_2301_path = pathlib.Path(__file__).parent / "bom-2301-complex.xml"
with open(_complex_bom_2301_path, "r") as f:
    sample_bom_2301_complex = f.read()
