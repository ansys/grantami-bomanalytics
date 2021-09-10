from typing import Union

from ansys.granta import bomanalytics
from ansys.granta.auth_common import AuthenticatedApiClient

from query_managers import MaterialQueryManager, PartQueryManager, SpecificationQueryManager, SubstanceQueryManager, \
    BoM1711QueryManager


class Connection:
    def __init__(self, url: str,
                 username: Union[str, None] = None,
                 password: Union[str, None] = None,
                 autologon: bool = False,
                 dbkey: Union[str, None] = None):
        # Create a generic AuthenticatedApiClient and initialize with the relevant models
        if autologon:
            self._client = AuthenticatedApiClient.with_autologon(servicelayer_url=url)
        else:
            self._client = AuthenticatedApiClient.with_credentials(servicelayer_url=url,
                                                                   username=username,
                                                                   password=password)
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
        if self.material_universe_table_name or \
                self.inhouse_materials_table_name or \
                self.specifications_table_name or \
                self.products_and_parts_table_name or \
                self.substances_table_name or \
                self.coatings_table_name:
            config = \
                bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig(self.material_universe_table_name,
                                                                                    self.inhouse_materials_table_name,
                                                                                    self.specifications_table_name,
                                                                                    self.products_and_parts_table_name,
                                                                                    self.substances_table_name,
                                                                                    self.coatings_table_name)
            return config

    def get_yaml(self):
        return self._documentation_api.get_miservicelayer_bom_analytics_v1svc_yaml()

    def create_material_query(self) -> MaterialQueryManager:
        query = MaterialQueryManager(connection=self)
        query.set_impacted_substance_api(self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials)
        query.set_compliance_api(self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_materials)
        return query

    def create_part_query(self) -> PartQueryManager:
        query = PartQueryManager(connection=self)
        query.set_impacted_substance_api(self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts)
        query.set_compliance_api(self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_parts)
        return query

    def create_specification_query(self) -> SpecificationQueryManager:
        query = SpecificationQueryManager(connection=self)
        query.set_impacted_substance_api(self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications)
        query.set_compliance_api(self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_specifications)
        return query

    def create_substance_query(self) -> SubstanceQueryManager:
        query = SubstanceQueryManager(connection=self)
        query.set_compliance_api(self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_substances)
        return query

    def create_bom_query(self) -> BoM1711QueryManager:
        query = BoM1711QueryManager(connection=self)
        query.set_impacted_substance_api(self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711)
        query.set_compliance_api(self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_bom1711)
        return query
