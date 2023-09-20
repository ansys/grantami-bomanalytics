from ._connection import Connection
from ._exceptions import GrantaMIException
from ._bom_helper import BoMHandler

from importlib import metadata as metadata

__version__ = metadata.version("ansys-grantami-bomanalytics")
