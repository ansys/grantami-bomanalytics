from ._connection import Connection
from ._exceptions import GrantaMIException

try:
    from importlib import metadata as metadata

    __version__ = metadata.version("ansys-grantami-bomanalytics")
except ImportError:
    from importlib_metadata import metadata as metadata_backport  # type: ignore[import]

    __version__ = metadata_backport("ansys-grantami-bomanalytics")["version"]
