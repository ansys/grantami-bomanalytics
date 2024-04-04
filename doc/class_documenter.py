from inspect import getmodule
from typing import Any, Optional

from sphinx.ext.autodoc import (
    Documenter,
    MethodDocumenter,
    ModuleAnalyzer,
    PropertyDocumenter,
    member_order_option,
)
from sphinx.ext.autodoc import ClassDocumenter as DefaultClassDocumenter


class CustomOrderException(Exception):
    pass


CUSTOM_ORDER_KEY = "by_mro_by_source"


class ClassDocumenter(DefaultClassDocumenter):
    # The only customization is to intercept the sort_members method and, only if the class being documented is
    # configured to use the custom member-order, to sort the member documenters according to the class MRO.

    def sort_members(self, documenters: list[tuple[Documenter, bool]],
                     order: str) -> list[tuple[Documenter, bool]]:
        # Intercept sorting only for classes configured with the custom member-order value
        if order != CUSTOM_ORDER_KEY:
            return super().sort_members(documenters, order)

        sorted_documenters = []
        # Traversing MRO in reverse, so that the resulting documentation includes members inherited
        # from the furthest ancestors first.
        for ancestor_kls in reversed([kls for kls in self.object.__mro__]):
            ancestor_kls_member_documenters = []
            for documenter, _isattr in documenters:
                member_fullname = self._read_documenter_object_name(documenter)
                member_kls_name, member_name = member_fullname.split(".")
                if member_kls_name == ancestor_kls.__qualname__:
                    ancestor_kls_member_documenters.append((documenter, _isattr))

            # If any documenters have been identified for an ancestor class, sort them by the source order
            if ancestor_kls_member_documenters:
                # Cannot delegate to super().sort_members to sort by source, because analyzer.tagorder identifies
                # object by `BaseClass.method`, whereas the documenters identify objects by `ConcreteClass.method`.
                # So we reuse the `super().sort_members` logic, but substitute the class name before looking up the
                # member position in the source code.

                # Block mostly copied from Documenter.sort_members
                if getmodule(self.object).__name__ == getmodule(ancestor_kls).__name__:
                    tagorder = self.analyzer.tagorder
                else:
                    # parent class not defined in current module, instantiate analyzer for ancestor class source module
                    analyzer = ModuleAnalyzer.for_module(getmodule(ancestor_kls).__name__)
                    analyzer.analyze()
                    tagorder = analyzer.tagorder

                def keyfunc(entry: tuple[Documenter, bool]) -> int:
                    fullname = entry[0].name.split('::')[1]
                    # Substitute the parent name with the base class name
                    fullname_in_mro = fullname.replace(self.object_name, ancestor_kls.__qualname__)
                    order = tagorder.get(fullname_in_mro, None)
                    if order is None:
                        raise CustomOrderException(
                            f"Error when processing {self.name}, unable to evaluate source order for {fullname_in_mro}"
                        )
                    return order

                sorted_by_parent_source = sorted(ancestor_kls_member_documenters, key=keyfunc)
                sorted_documenters.extend(sorted_by_parent_source)
        return sorted_documenters

    def _read_documenter_object_name(self, documenter: Documenter) -> str:
        if isinstance(documenter, MethodDocumenter):
            documenter.parse_name()
            documenter.import_object(True)
            return documenter.object.__qualname__
        elif isinstance(documenter, PropertyDocumenter):
            documenter.parse_name()
            documenter.import_object(True)
            return documenter.object.fget.__qualname__
        else:
            raise CustomOrderException(
                f"Error when processing {self.name}. Member {documenter.name} is of type {type(documenter)}, "
                f"which is not supported. Supported member types are property and method."
            )


def wrapped_member_order_option(arg: Any) -> Optional[str]:
    """Used to convert the :member-order: option to auto directives."""
    # Allow extra configuration value for member order.
    if arg == CUSTOM_ORDER_KEY:
        return arg
    else:
        return member_order_option(arg)


# Allow custom member-order setting
ClassDocumenter.option_spec['member-order'] = wrapped_member_order_option
