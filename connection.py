from typing import Union

from ansys.granta import bomanalytics
from ansys.granta.auth_common import AuthenticatedApiClient

from builders import MaterialQueryBuilder, PartQueryBuilder, SpecificationQueryBuilder, SubstanceQueryBuilder, \
    BoM1711QueryBuilder
from item_references import MaterialReference, PartReference, SpecificationReference, SubstanceReference, \
    BoM1711Reference


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

    def create_material_query(self):
        query = MaterialQueryBuilder(self)
        query._item_type = MaterialReference
        query._item_type_name = 'materials'
        query.set_compliance_endpoints(bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest,
                                       self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_materials)
        query.set_impacted_substances_endpoints(
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest,
            self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials)
        return query

    def create_part_query(self):
        query = PartQueryBuilder(self)
        query.set_item_type(PartReference, 'parts')
        query.set_compliance_endpoints(bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest,
                                       self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_parts)
        query.set_impacted_substances_endpoints(
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest,
            self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts)
        return query

    def create_specification_query(self):
        query = SpecificationQueryBuilder(self)
        query.set_item_type(SpecificationReference, 'specifications')
        query.set_compliance_endpoints(
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest,
            self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_specifications)
        query.set_impacted_substances_endpoints(
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest,
            self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications)
        return query

    def create_substance_query(self):
        query = SubstanceQueryBuilder(self)
        query.set_item_type(SubstanceReference, 'substances')
        query.set_compliance_endpoints(
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest,
            self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_substances)
        return query

    def create_bom_query(self):
        query = BoM1711QueryBuilder(self)
        query.set_item_type(BoM1711Reference, 'bom')
        query.set_compliance_endpoints(bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request,
                                       self.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_bom1711)
        query.set_impacted_substances_endpoints(
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request,
            self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711)
        return query
