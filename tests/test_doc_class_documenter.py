# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock

DOC_DIR = Path(__file__).resolve().parents[1] / "doc"
sys.path.insert(0, str(DOC_DIR))

import class_documenter


def test_wrapped_member_order_option_accepts_custom_value():
    assert class_documenter.wrapped_member_order_option(class_documenter.CUSTOM_ORDER_KEY) == class_documenter.CUSTOM_ORDER_KEY


def test_register_custom_member_order_option_handles_missing_class_entry(monkeypatch):
    monkeypatch.setattr(class_documenter, "_OPTION_SPECS", {})

    class_documenter.register_custom_member_order_option()

    assert (
        class_documenter._OPTION_SPECS[class_documenter.ClassDocumenter.objtype]["member-order"]
        is class_documenter.wrapped_member_order_option
    )


def test_register_custom_class_documenter_uses_app_registry():
    registry = SimpleNamespace(add_documenter=Mock())
    app = SimpleNamespace(registry=registry)

    class_documenter.register_custom_class_documenter(app)

    registry.add_documenter.assert_called_once_with(
        class_documenter.ClassDocumenter.objtype,
        class_documenter.ClassDocumenter,
    )


def test_register_custom_class_documenter_can_be_called_multiple_times():
    registry = SimpleNamespace(add_documenter=Mock())
    app = SimpleNamespace(registry=registry, add_autodocumenter=Mock())

    class_documenter.register_custom_class_documenter(app)
    class_documenter.register_custom_class_documenter(app)

    assert registry.add_documenter.call_count == 2
    app.add_autodocumenter.assert_not_called()


def test_register_custom_class_documenter_falls_back_to_add_autodocumenter():
    app = SimpleNamespace(add_autodocumenter=Mock())

    class_documenter.register_custom_class_documenter(app)

    app.add_autodocumenter.assert_called_once_with(class_documenter.ClassDocumenter, override=True)


def test_register_custom_class_documenter_falls_back_when_registry_lacks_add_documenter():
    app = SimpleNamespace(registry=SimpleNamespace(), add_autodocumenter=Mock())

    class_documenter.register_custom_class_documenter(app)

    app.add_autodocumenter.assert_called_once_with(class_documenter.ClassDocumenter, override=True)
