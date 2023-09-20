from pathlib import Path
from typing import TYPE_CHECKING
import xmlschema
from xmlschema import XMLSchema
from ansys.grantami.bomanalytics.bom_types import BoMReader, BoMWriter

if TYPE_CHECKING:
    from ansys.grantami.bomanalytics.bom_types._bom_types import BillOfMaterials

class BoMHandler:
    _schema_path: Path = Path(__file__).parent / "schemas" / "BillOfMaterialsEco2301.xsd"
    _schema: XMLSchema

    def __init__(self):
        """
        Handler for XML formatted BoMs, supports reading from files and strings, and serializing to string format.
        """
        self._schema = XMLSchema(self._schema_path)
        self._schema.namespaces[""] = self._schema.namespaces["eco"]
        self._reader = BoMReader(self._schema)
        self._writer = BoMWriter(self._schema)

    def load_bom_from_file(self, file_path: Path) -> "BillOfMaterials":
        """
        Read a BoM from a file and return the corresponding BillOfMaterials object for use

        Parameters
        ----------
        file_path: Path
            Location of the BoM XML file

        Returns
        -------
        BillOfMaterials
        """
        with open(file_path, "r", encoding="utf8") as fp:
            obj, errors = self._schema.decode(fp, validation="lax")

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")
        print(obj)

        return self._reader.read_bom(obj)

    def load_bom_from_text(self, bom_text: str) -> "BillOfMaterials":
        """
        Read a BoM from a string and return the corresponding BillOfMaterials object for use

        Parameters
        ----------
        bom_text: str
            String object containing an XML representation of a BoM

        Returns
        -------
        BillOfMaterials
        """
        obj, errors = self._schema.decode(bom_text, validation="lax", keep_empty=True)

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        return self._reader.read_bom(obj)

    def dump_bom(self, bom: "BillOfMaterials") -> str:
        """
        Convert a BillOfMaterials object into a string XML representation

        Parameters
        ----------
        bom: BillOfMaterials

        Returns
        -------
        str
            Serialized representation of the BoM
        """
        bom_dict = self._writer.convert_bom_to_dict(bom)
        obj, errors = self._schema.encode(bom_dict, validation="lax", unordered=True)

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM object:\n{newline.join([error.msg for error in errors])}")

        return xmlschema.etree_tostring(obj)
