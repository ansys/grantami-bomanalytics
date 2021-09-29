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

    def __init__(
        self,
        servicelayer_url: str,
    ):
        super().__init__(servicelayer_url=servicelayer_url)
        self._documentation_api: Union[bomanalytics.DocumentationApi, None] = None
        self.compliance_api: Union[bomanalytics.ComplianceApi, None] = None
        self.impacted_substances_api: Union[bomanalytics.ImpactedSubstancesApi, None] = None

    def build(self) -> ApiClient:
        client = super().build()
        client.setup_client(bomanalytics.models)
        return client
