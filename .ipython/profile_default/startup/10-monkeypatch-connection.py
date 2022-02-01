import os
from ansys.grantami.bomanalytics import Connection
from ansys.grantami.bomanalytics._connection import BOMAnalyticsClient

# Monkey patch the Connection() class to use the environment variable-specified server URL.
original_ctor = Connection.__init__


def new_init(self: Connection, _):
    original_ctor(self, os.getenv("TEST_SL_URL"))


Connection.__init__ = new_init

# Monkey patch the Connection builder methods to use the environment variable-specified credentials.
Connection.with_creds_original = Connection.with_credentials


def with_credentials(self: Connection, _, __) -> Connection:
    user_name = os.getenv("TEST_USER")
    password = os.getenv("TEST_PASS")
    return self.with_creds_original(user_name, password)


def with_autologon(self: Connection) -> Connection:
    return self.with_credentials("foo", "bar")


Connection.with_credentials = with_credentials
Connection.with_autologon = with_autologon


# Monkey patch the Client object to report the url specified in the code, or the one below if not overridden
server_url = "http://my_grantami_server/mi_servicelayer"


def __repr__(self: BOMAnalyticsClient) -> str:
    return f'<BomServicesClient: url="{server_url}", dbkey="{self._db_key}">'


BOMAnalyticsClient.__repr__ = __repr__
