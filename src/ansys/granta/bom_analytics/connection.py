from typing import Union

from ansys.granta import bomanalytics
from ansys.granta.auth_common import ApiClient


class Connection:
    """
    Connection to an instance of Granta MI.

    Parameters
    ----------
    url : str
        Location of the Granta MI Service layer.
    dbkey : str
        Database key of the Restricted Substances-based database.
    username, password : str, optional
        Credentials to be used for Basic or Windows authentication. Not required if autologon is used.
    autologon : bool : default=False
        Attempt to use the current user's Windows session to authenticate.

    Attributes
    ----------
    material_universe_table_name : str
        Specify an alternate name for the 'MaterialUniverse' table
    inhouse_materials_table_name : str
        Specify an alternate name for the 'Materials - in house' table
    specifications_table_name : str
        Specify an alternate name for the 'Specifications' table
    products_and_parts_table_name : str
        Specify an alternate name for the 'Products and parts' table
    substances_table_name : str
        Specify an alternate name for the 'Restricted Substances' table
    coatings_table_name : str
        Specify an alternate name for the 'Coatings' table

    Returns
    -------
    Connection
        Object representing the connection to Granta MI.

    Examples
    --------
    >>> Connection(url='http://localhost/mi_servicelayer', autologon=True)

    >>> Connection(url='http://localhost/mi_servicelayer', username='my_username', password='my_password')
    """

    def __init__(
        self,
        client: ApiClient,
        db_key: str,
    ):
        self._client = client
        self._client.setup_client(bomanalytics.models)

        self._documentation_api = bomanalytics.DocumentationApi(self._client)
        self.compliance_api = bomanalytics.ComplianceApi(self._client)
        self.impacted_substances_api = bomanalytics.ImpactedSubstancesApi(self._client)

        self._db_key = db_key

        self.material_universe_table_name: Union[str, None] = None
        self.in_house_materials_table_name: Union[str, None] = None
        self.specifications_table_name: Union[str, None] = None
        self.products_and_parts_table_name: Union[str, None] = None
        self.substances_table_name: Union[str, None] = None
        self.coatings_table_name: Union[str, None] = None

    @property
    def db_key(self) -> str:
        return self._db_key

    @property
    def query_config(
        self,
    ) -> bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig:
        if (
            self.material_universe_table_name
            or self.in_house_materials_table_name
            or self.specifications_table_name
            or self.products_and_parts_table_name
            or self.substances_table_name
            or self.coatings_table_name
        ):
            config = (
                bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig(
                    self.material_universe_table_name,
                    self.in_house_materials_table_name,
                    self.specifications_table_name,
                    self.products_and_parts_table_name,
                    self.substances_table_name,
                    self.coatings_table_name,
                )
            )
            return config

    def get_yaml(self) -> str:
        return self._documentation_api.get_miservicelayer_bom_analytics_v1svc_yaml()
