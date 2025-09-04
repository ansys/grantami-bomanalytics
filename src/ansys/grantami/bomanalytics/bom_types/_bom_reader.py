# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import inspect
from types import ModuleType
from typing import Any, Dict, Generic, Iterable, Type, TypeVar

from xmlschema import XMLSchema

from ._base_types import BaseType, QualifiedXMLName

TBom = TypeVar("TBom", bound=BaseType)
TAny = TypeVar("TAny", bound=BaseType)


class _GenericBoMReader(Generic[TBom]):
    _namespaces: dict[str, str]
    _class_members: Dict[str, Type[BaseType]]
    _bom_type: Type[TBom]
    _schema: XMLSchema

    def __init_subclass__(cls, xml_type_modules: list[ModuleType], bom_type: Type[TBom]):
        """
        Bind this generic class to a specific set of xml types and target BoM type.

        xml_type_modules : list[ModuleType]
            A list of modules for which the contained classes should be registered as XML types.
        bom_type : Type[TBom]
            The BillOfMaterials type that this class can convert dictionaries to.
        """
        cls._class_members = {}
        for xml_type_module in xml_type_modules:
            cls._class_members.update({k: v for k, v in inspect.getmembers(xml_type_module, inspect.isclass)})
        cls._bom_type = bom_type

    def __init__(self, schema: XMLSchema):
        """
        Reader to convert a JSON formatted BoM, created by xmlschema, into a populated BillOfMaterials object.

        The target BillOfMaterials type is defined by the _bom_type class attribute.

        Parameters
        ----------
        schema: XMLSchema
            Parsed XMLSchema representing a valid Eco BoM format
        """
        self._namespaces: Dict[str, str] = {}
        # Used to track fields in an object that haven't been deserialized.
        self.__undeserialized_fields: list[str] = []
        self._schema = schema

    @property
    def target_namespace(self) -> str:
        """The target namespace of the loaded XML schema.

        Returns
        -------
        str
        """
        return self._schema.target_namespace

    def read_bom(self, obj: Dict) -> tuple[TBom, list]:
        """
        Convert a BoM object from xmlschema JSON format into a BillOfMaterials object.

        Parameters
        ----------
        obj: Dict
            Source xmlschema JSON format object

        Returns
        -------
        tuple[TBom, list]
            A tuple containing the converted BillOfMaterials object, and any fields in the obj argument that could not
            be deserialized.
        """
        namespaces = {}
        for k, v in obj.items():
            if k == "@xmlns":
                namespaces[""] = v
            elif k.startswith("@xmlns"):
                _, prefix = k.split(":")
                namespaces[prefix] = v

        self._namespaces = namespaces

        bom = self._create_type(self._bom_type, obj)
        return bom, self.__undeserialized_fields

    def create_type(self, type_name: str, obj: Dict) -> BaseType:
        """
        Recursively deserialize a dictionary of XML fields to a hierarchy of Python objects.

        Keeps track of any fields which have not been deserialized, so they can be optionally reported to the user
        following deserialization.

        Parameters
        ----------
        type_name : str
            Name of the current type to populate.
        obj : dict
            The data to use to populate the new type.
        """

        target_type = self._class_members[type_name]
        return self._create_type(target_type, obj)

    def _create_type(self, type_: Type[TAny], obj: Dict) -> TAny:
        local_obj = obj.copy()

        kwargs = {}
        for target_type, target_property_name, field_name in type_._props:
            kwargs.update(self._deserialize_single_type(local_obj, target_type, target_property_name, field_name))
        for target_type, target_property_name, container_name, item_name in type_._list_props:
            kwargs.update(
                self._deserialize_list_type(local_obj, target_type, target_property_name, container_name, item_name)
            )
        for target, field_name in type_._simple_values:
            field_obj = self.get_field(local_obj, field_name)
            kwargs[target] = field_obj
        kwargs.update(type_._process_custom_fields(local_obj, self))
        self._append_unserialized_fields(type_.__name__, local_obj)
        instance = type_(**kwargs)
        return instance

    def _deserialize_list_type(
        self,
        obj: Dict,
        target_type: str,
        target_property_name: str,
        container_name: QualifiedXMLName,
        item_name: QualifiedXMLName,
    ) -> Dict[str, Iterable]:
        container_obj = self.get_field(obj, container_name)
        if container_obj is not None:
            items_obj = self.get_field(container_obj, item_name)
            if items_obj is not None and len(items_obj) > 0:
                return {target_property_name: [self.create_type(target_type, item_dict) for item_dict in items_obj]}
        return {}

    def _deserialize_single_type(
        self,
        obj: Dict,
        target_type: str,
        target_property_name: str,
        field_name: QualifiedXMLName,
    ) -> Dict[str, Any]:
        field_obj = self.get_field(obj, field_name)
        if field_obj is not None:
            return {target_property_name: self.create_type(target_type, field_obj)}
        return {}

    def _append_unserialized_fields(self, type_name: str, obj: Dict) -> None:
        for k, v in obj.items():
            if not k.startswith("@xmlns"):
                val = f"{str(v)[:100]}..." if len(str(v)) > 100 else str(v)
                msg = f'Parent type "{type_name}", field "{k}" with value "{val}".'
                self.__undeserialized_fields.append(msg)

    def get_field(self, obj: Dict, field_name: QualifiedXMLName) -> Any:
        """
        Given an object and a qualified name, determines the qualified field name to fetch based on the document
        namespace tags.

        If a field is found that matches the specified local name and namespace, the value is deleted from the
        dictionary.

        Parameters
        ----------
        obj: Dict
            The source dictionary with the data to be deserialized.
        field_name: QualifiedXMLName
            Fully qualified name of the target field.
        """
        for k, v in obj.items():
            if k.startswith("@xmlns"):
                continue

            if k == "$" and field_name.local_name == "$":
                del obj[k]
                return v

            if k.startswith("@"):
                is_matched = self._match_attribute(k, field_name)
                if is_matched:
                    del obj[k]
                    return v
            else:
                is_matched = self._match_element(k, field_name)
                if is_matched:
                    del obj[k]
                    return v
        return None

    def _match_element(self, item_name: str, match_name: QualifiedXMLName) -> bool:
        if ":" not in item_name:
            return match_name.namespace == self._namespaces.get("", None) and item_name == match_name.local_name
        namespace_prefix, stripped_name = item_name.split(":")
        field_namespace_url = self._namespaces[namespace_prefix]
        return match_name.namespace == field_namespace_url and stripped_name == match_name.local_name

    def _match_attribute(self, item_name: str, match_name: QualifiedXMLName) -> bool:
        if not item_name.startswith("@"):
            return False
        if ":" not in item_name:
            if "" in self._namespaces:
                return match_name.namespace == self._namespaces[""] and item_name == match_name.local_name
            else:
                # Workaround for https://github.com/ansys/grantami-bomanalytics-private/issues/75
                # TODO - check item_name's parent item namespace against match_name.namespace
                return item_name == match_name.local_name
        item_name = item_name[1:]
        namespace_prefix, stripped_name = item_name.split(":")
        stripped_name = f"@{stripped_name}"
        field_namespace_url = self._namespaces[namespace_prefix]
        return match_name.namespace == field_namespace_url and stripped_name == match_name.local_name
