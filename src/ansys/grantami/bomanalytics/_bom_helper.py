from pathlib import Path
from typing import TYPE_CHECKING

import xmlschema  # type: ignore[import]
from xmlschema import XMLSchema

from .bom_types import BoMReader, BoMWriter
from .schemas import bom_schema_2301

if TYPE_CHECKING:
    from .bom_types import BillOfMaterials


class BoMHandler:
    """
    Handler for XML formatted BoMs, supports reading from files and strings, and serializing to string format.
    """

    _schema_path: Path = bom_schema_2301
    _schema: XMLSchema

    def __init__(self) -> None:
        self._schema = XMLSchema(self._schema_path)
        self._schema.namespaces[""] = self._schema.namespaces["eco"]
        self._reader = BoMReader(self._schema)
        self._writer = BoMWriter(self._schema)

    def load_bom_from_file(self, file_path: Path) -> "BillOfMaterials":
        """
        Read a BoM from a file and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        file_path : :class:`~pathlib.Path`
            Location of the BoM XML file.

        Returns
        -------
        :class:`~._bom_types.BillOfMaterials`
        """
        with open(file_path, "r", encoding="utf8") as fp:
            obj, errors = self._schema.decode(fp, validation="lax")

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        assert isinstance(obj, dict)

        return self._reader.read_bom(obj)

    def load_bom_from_text(self, bom_text: str) -> "BillOfMaterials":
        """
        Read a BoM from a string and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        bom_text : str
            String object containing an XML representation of a BoM.

        Returns
        -------
        :class:`~._bom_types.BillOfMaterials`
        """
        obj, errors = self._schema.decode(bom_text, validation="lax", keep_empty=True)

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        assert isinstance(obj, dict)

        return self._reader.read_bom(obj)

    def dump_bom(self, bom: "BillOfMaterials") -> str:
        """
        Convert a BillOfMaterials object into a string XML representation.

        Parameters
        ----------
        bom : :class:`~._bom_types.BillOfMaterials`

        Returns
        -------
        str
            Serialized representation of the BoM.
        """
        bom_dict = self._writer.convert_bom_to_dict(bom)
        obj, errors = self._schema.encode(
            bom_dict, validation="lax", namespaces=self._schema.namespaces, unordered=True
        )

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM object:\n{newline.join([error.msg for error in errors])}")

        output = xmlschema.etree_tostring(obj)
        assert isinstance(output, str)
        return output
