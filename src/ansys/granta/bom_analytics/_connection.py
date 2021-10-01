from typing import Union

from ansys.granta import bomanalytics
from ansys.granta.auth_common import ApiClientFactory, ApiClient


class Connection(ApiClientFactory):
    """
    Build a connection to an instance of Granta MI.

    Parameters
    ----------
    servicelayer_url : str
        The url to the Granta MI service layer

    Examples
    --------
    >>> conn = Connection(servicelayer_url="http://my_mi_server/mi_servicelayer").with_autologon().build()

    >>> conn = Connection(servicelayer_url="http://my_mi_server/mi_servicelayer") \
    ...     .with_credentials(username="my_username", password="my_password") \
    ...     .build()
    """

    def build(self) -> ApiClient:
        client = super().build()
        client.setup_client(bomanalytics.models)
        return client
