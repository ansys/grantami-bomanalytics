from ._connection import Connection
from ._exceptions import GrantaMIException

_PACKAGE_NAME = "ansys-grantami-bomanalytics"

try:
    from importlib import metadata as metadata

    __version__ = metadata.version(_PACKAGE_NAME)
except ImportError:
    from importlib_metadata import metadata as metadata_backport  # type: ignore[import]

    __version__ = metadata_backport(_PACKAGE_NAME)["version"]
