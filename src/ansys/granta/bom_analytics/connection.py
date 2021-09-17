from typing import Union

from ansys.granta import bomanalytics
from ansys.granta.auth_common import AuthenticatedApiClient


class Connection:
    def __init__(
        self,
        url: str,
        dbkey: str,
        username: Union[str, None] = None,
        password: Union[str, None] = None,
        autologon: bool = False,
    ):
        # TODO: Support all options
        if autologon:
            self._client = AuthenticatedApiClient.with_autologon(servicelayer_url=url)
        else:
            self._client = AuthenticatedApiClient.with_credentials(
                servicelayer_url=url, username=username, password=password
            )
        self._client.setup_client(bomanalytics.models)

        self._documentation_api = bomanalytics.DocumentationApi(self._client)
        self.compliance_api = bomanalytics.ComplianceApi(self._client)
        self.impacted_substances_api = bomanalytics.ImpactedSubstancesApi(self._client)

        self.dbkey = dbkey

        self.material_universe_table_name: Union[str, None] = None
        self.inhouse_materials_table_name: Union[str, None] = None
        self.specifications_table_name: Union[str, None] = None
        self.products_and_parts_table_name: Union[str, None] = None
        self.substances_table_name: Union[str, None] = None
        self.coatings_table_name: Union[str, None] = None

    @property
    def query_config(self):
        if (
            self.material_universe_table_name
            or self.inhouse_materials_table_name
            or self.specifications_table_name
            or self.products_and_parts_table_name
            or self.substances_table_name
            or self.coatings_table_name
        ):
            config = (
                bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig(
                    self.material_universe_table_name,
                    self.inhouse_materials_table_name,
                    self.specifications_table_name,
                    self.products_and_parts_table_name,
                    self.substances_table_name,
                    self.coatings_table_name,
                )
            )
            return config

    def get_yaml(self):
        return self._documentation_api.get_miservicelayer_bom_analytics_v1svc_yaml()
