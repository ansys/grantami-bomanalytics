from importlib import metadata as metadata

from ._connection import Connection
from ._exceptions import GrantaMIException
from ._bom_helper import BoMHandler

__version__ = metadata.version("ansys-grantami-bomanalytics")
