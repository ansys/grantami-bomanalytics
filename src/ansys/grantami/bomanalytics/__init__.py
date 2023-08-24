from ._connection import Connection
from ._exceptions import GrantaMIException

from importlib import metadata as metadata

__version__ = metadata.version("ansys-grantami-bomanalytics")
