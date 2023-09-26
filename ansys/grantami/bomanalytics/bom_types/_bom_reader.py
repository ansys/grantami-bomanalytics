import inspect
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Type, cast

from xmlschema import XMLSchema  # type: ignore[import]

from . import _bom_types as bom_types
from ._bom_types import BaseType

if TYPE_CHECKING:
    from . import BaseType, BillOfMaterials, HasNamespace


class BoMReader:
    _schema: XMLSchema
    _class_members: Dict[str, Type[BaseType]]

    def __init__(self, schema: XMLSchema):
        """
        Reader to convert a JSON formatted BoM, created by xmlschema, into populated BillOfMaterials object.

        Parameters
        ----------
        schema: XMLSchema
            Parsed XMLSchema representing the 2301 Eco BoM format
        """
        self._schema = schema
        self._namespaces: Dict[str, str] = {}
        self._class_members: Dict[str, Type[BaseType]] = {
            k: v for k, v in inspect.getmembers(bom_types, inspect.isclass)
        }

    def read_bom(self, obj: Dict) -> "BillOfMaterials":
        """
        Convert a BoM object from xmlschema JSON format into a BillOfMaterials object.

        Parameters
        ----------
        obj: Dict
            Source xmlschema JSON format object

        Returns
        -------
        BillOfMaterials
        """
        namespaces = {}
        for k, v in obj.items():
            if k == "@xmlns":
                namespaces[""] = v
            elif k.startswith("@xmlns"):
                _, prefix = k.split(":")
                namespaces[prefix] = v

        self._namespaces = namespaces

        return cast("BillOfMaterials", self.create_type("BillOfMaterials", obj))

    def create_type(self, type_name: str, obj: Dict) -> "BaseType":
        type_ = self._class_members[type_name]
        kwargs = {}
        for target_type, target_property_name, field_name in type_._props:
            kwargs.update(self._deserialize_single_type(type_, obj, target_type, target_property_name, field_name))
        for target_type, target_property_name, container_name, container_namespace, field_name in type_._list_props:
            kwargs.update(
                self._deserialize_list_type(
                    type_, obj, target_type, target_property_name, container_name, container_namespace, field_name
                )
            )
        for target, source in type_._simple_values:
            field_obj = self.get_field(type_, obj, source)
            kwargs[target] = field_obj
        kwargs.update(type_._process_custom_fields(obj, self))
        instance = self._class_members[type_name](**kwargs)
        return instance

    def _deserialize_list_type(
        self,
        instance: "Type[BaseType]",
        obj: Dict,
        target_type: str,
        target_property_name: str,
        container_name: str,
        container_namespace: str,
        item_name: str,
    ) -> Dict[str, Iterable]:
        container_obj = self.get_field(instance, obj, container_name)
        if container_obj is not None:
            items_obj = self.get_field(instance, container_obj, item_name, container_namespace)
            if items_obj is not None and len(items_obj) > 0:
                return {target_property_name: [self.create_type(target_type, item_dict) for item_dict in items_obj]}
        return {}

    def _deserialize_single_type(
        self, instance: "Type[BaseType]", obj: Dict, target_type: str, target_property_name: str, field_name: str
    ) -> Dict[str, Any]:
        field_obj = self.get_field(instance, obj, field_name)
        if field_obj is not None:
            return {target_property_name: self.create_type(target_type, field_obj)}
        return {}

    def get_field(
        self, instance: "Type[HasNamespace]", obj: Dict, field_name: str, namespace_url: Optional[str] = None
    ) -> Any:
        """
        Given an object and a local name, determines the qualified field name to fetch based on the document namespace
        tags.

        Parameters
        ----------
        instance: BaseType
            The object being deserialized into, the namespace will be used from this object by default
        obj: Dict
            The source dictionary with the data to be deserialized.
        field_name: str
            Local name of the target field.
        namespace_url: Optional[str]
            If the target namespace is different from that of the target object, for example if the type defines an
            anonymous complex type, it can be overridden here.
        """
        if namespace_url is None:
            namespace_url = instance._namespace
        for k, v in obj.items():
            if k.startswith("@xmlns"):
                continue
            if ":" not in k:
                if "" in self._namespaces and namespace_url == self._namespaces[""] and k == field_name:
                    return v
            else:
                is_attribute = False
                item_name = k
                if item_name.startswith("@"):
                    item_name = item_name[1:]
                    is_attribute = True
                namespace_prefix, stripped_name = item_name.split(":")
                if is_attribute:
                    stripped_name = f"@{stripped_name}"
                field_namespace_url = self._namespaces[namespace_prefix]
                if namespace_url == field_namespace_url and stripped_name == field_name:
                    return v
        return None
