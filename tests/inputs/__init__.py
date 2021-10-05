import pathlib
from .examples import examples_as_strings, examples_as_dicts

_bom_path = pathlib.Path(__file__).parent / "bom.xml"
with open(_bom_path, "r") as f:
    sample_bom = f.read()
