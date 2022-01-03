import pathlib
from .examples import examples_as_strings, examples_as_dicts

_bom_path = pathlib.Path(__file__).parent / "bom.xml"
with open(_bom_path, "r") as f:
    sample_bom = f.read()

_complex_bom_path = pathlib.Path(__file__).parent / "bom-complex.xml"
with open(_complex_bom_path, "r") as f:
    sample_bom_complex = f.read()

sample_bom_custom_db = sample_bom_complex.replace("MI_Restricted_Substances", "MI_Restricted_Substances_Custom_Tables")
