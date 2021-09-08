from ansys.granta import bomanalytics
from ansys.granta.auth_common import AuthenticatedApiClient
from typing import Union, List, Dict
from abc import ABC, abstractmethod
from enum import Enum


class TableType(Enum):
    unknown = -1
    material = 0
    part = 1
    specification = 2
    substance = 3
    coating = 4


MATERIAL_UNIVERSE_DEFAULT_NAME = 'MaterialUniverse'
INHOUSE_MATERIALS_DEFAULT_NAME = 'In-house materials'
SPECIFICATIONS_DEFAULT_NAME = 'Specifications'
PRODUCTS_AND_PARTS_DEFAULT_NAME = 'Products and parts'
SUBSTANCES_DEFAULT_NAME = 'Substances'
COATINGS_DEFAULT_NAME = 'Coatings'


class Indicator(ABC):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        self._name = name
        self._legislation_names = legislation_names
        self._default_threshold_percentage = default_threshold_percentage
        self._indicator_type = None

    @property
    def definition(self):
        return bomanalytics.\
            GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(name=self._name,
                                                                         legislation_names=self._legislation_names,
                                                                         default_threshold_percentage=self._default_threshold_percentage,
                                                                         type=self._indicator_type)


class RoHSIndicator(Indicator):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = 'Rohs'


class WatchListIndicator(Indicator):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = 'WatchList'


class _BoMReference(ABC):
    def __init__(self, record_history_identity: int, record_guid: str, record_history_guid: str):
        self._record_history_identity = record_history_identity
        self._record_guid = record_guid
        self._record_history_guid = record_history_guid
        self._model = None

    def _create_definition(self):
        if self._record_history_identity:
            return self._model(reference_type="MiRecordHistoryIdentity", reference_value=self._record_history_identity)
        if self._record_guid:
            return self._model(reference_type="MiRecordGuid", reference_value=self._record_guid)
        if self._record_history_guid:
            return self._model(reference_type="MiRecordHistoryGuid", reference_value=self._record_history_guid)

    @property
    @abstractmethod
    def definition(self):
        pass


class _PartReference(_BoMReference):
    def __init__(self,
                 part_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._part_id = part_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonPartReference

    @property
    def definition(self):
        definition = super()._create_definition() or self._model(reference_type="PartId", reference_value=self._part_id)
        return definition


class _MaterialReference(_BoMReference):
    def __init__(self,
                 material_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._material_id = material_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference

    @property
    def definition(self):
        definition = super()._create_definition() or \
                     self._model(reference_type="MaterialId", reference_value=self._material_id)
        return definition


class _SpecificationReference(_BoMReference):
    def __init__(self,
                 specification_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._specification_id = specification_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference

    @property
    def definition(self):
        definition = super()._create_definition() or \
                     self._model(reference_type="SpecificationId", reference_value=self._specification_id)
        return definition


class _SubstanceReference(_BoMReference):
    def __init__(self,
                 substance_name=None,
                 cas_number=None,
                 ec_number=None,
                 record_history_identity=None,
                 record_guid=None,
                 record_history_guid=None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._substance_name = substance_name
        self._cas_number = cas_number
        self._ec_number = ec_number
        self._percentage_threshold = None
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount

    @property
    def percentage_threshold(self) -> float:
        return self._percentage_threshold

    @percentage_threshold.setter
    def percentage_threshold(self, value: float):
        assert 0 < value < 100
        self._percentage_threshold = value

    @property
    def definition(self):
        if self._record_history_identity:
            return self._model(reference_type="MiRecordHistoryIdentity", reference_value=self._record_history_identity,
                               percentage_amount=self._percentage_threshold)
        if self._record_guid:
            return self._model(reference_type="MiRecordGuid", reference_value=self._record_guid,
                               percentage_amount=self._percentage_threshold)
        if self._record_history_guid:
            return self._model(reference_type="MiRecordHistoryGuid", reference_value=self._record_history_guid,
                               percentage_amount=self._percentage_threshold)
        if self._substance_name:
            return self._model(reference_type="SubstanceName", reference_value=self._substance_name,
                               percentage_amount=self._percentage_threshold)
        if self._cas_number:
            return self._model(reference_type="CasNumber", reference_value=self._cas_number,
                               percentage_amount=self._percentage_threshold)
        if self._ec_number:
            return self._model(reference_type="EcNumber", reference_value=self._ec_number,
                               percentage_amount=self._percentage_threshold)


class Connection:
    def __init__(self, url: str,
                 username: Union[str, None] = None,
                 password: Union[str, None] = None,
                 autologon: bool = False,
                 dbkey: Union[str, None] = None):
        # Create a generic AuthenticatedApiClient and initialize with the relevant models
        if autologon:
            self._client = AuthenticatedApiClient.with_autologon(servicelayer_url=url)
        self._client = AuthenticatedApiClient.with_credentials(servicelayer_url=url,
                                                               username=username,
                                                               password=password)
        self._client.setup_client(bomanalytics.models)

        self._documentation_api = bomanalytics.DocumentationApi(self._client)
        self._compliance_api = bomanalytics.ComplianceApi(self._client)
        self._impacted_substances_api = bomanalytics.ImpactedSubstancesApi(self._client)

        self.dbkey = dbkey

        self.material_universe_table_name: Union[str, None] = None
        self.inhouse_materials_table_name: Union[str, None] = None
        self.specifications_table_name: Union[str, None] = None
        self.products_and_parts_table_name: Union[str, None] = None
        self.substances_table_name: Union[str, None] = None
        self.coatings_table_name: Union[str, None] = None

    @property
    def _query_config(self):
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

    def create_query(self):
        return QueryBuilder(self)

    def get_yaml(self):
        return self._documentation_api.get_miservicelayer_bom_analytics_v1svc_yaml()

    def get_table_type(self, table_name: str):
        if self.material_universe_table_name and table_name == self.material_universe_table_name:
            return TableType.material
        if self.inhouse_materials_table_name and table_name == self.inhouse_materials_table_name:
            return TableType.material
        if self.specifications_table_name and table_name == self.specifications_table_name:
            return TableType.specification
        if self.products_and_parts_table_name and table_name == self.products_and_parts_table_name:
            return TableType.part
        if self.substances_table_name and table_name == self.substances_table_name:
            return TableType.substance
        if self.coatings_table_name and table_name == self.coatings_table_name:
            return TableType.coatings

        if table_name == MATERIAL_UNIVERSE_DEFAULT_NAME or table_name == INHOUSE_MATERIALS_DEFAULT_NAME:
            return TableType.material
        if table_name == SPECIFICATIONS_DEFAULT_NAME:
            return TableType.specification
        if table_name == PRODUCTS_AND_PARTS_DEFAULT_NAME:
            return TableType.part
        if table_name == SUBSTANCES_DEFAULT_NAME:
            return TableType.substance
        if table_name == COATINGS_DEFAULT_NAME:
            return TableType.coatings

        return TableType.unknown

    def get_impacted_substances_for_legislations(self, legislations, parts, specifications, materials):
        assert self.dbkey, "No DB Key specified"

        results = {}

        if materials:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest(
                database_key=self.dbkey,
                materials=materials,
                legislation_names=legislations)
            material_response = self._impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials(
                req)
            results = {**results, **material_response.to_dict()}
        if specifications:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest(
                database_key=self.dbkey,
                specifications=specifications,
                legislation_names=legislations)
            specification_response = self._impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications(
                req)
            results = {**results, **specification_response.to_dict()}
        if parts:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest(
                database_key=self.dbkey,
                parts=parts,
                legislation_names=legislations)
            part_response = self._impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts(
                req)
            results = {**results, **part_response.to_dict()}
        return results

    def get_compliance_for_indicators(self, indicators: List[Indicator], parts, specifications, materials, substances):
        assert self.dbkey, "No DB Key specified"

        indicator_objects = [i.definition for i in indicators]
        results = {}

        if materials:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest(
                database_key=self.dbkey,
                materials=materials,
                indicators=indicator_objects)
            material_response = self._compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_materials(req)
            results = {**results, **material_response.to_dict()}
        if parts:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest(database_key=self.dbkey,
                                                                                               parts=parts,
                                                                                               indicators=indicator_objects)
            part_response = self._compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_parts(req)
            results = {**results, **part_response.to_dict()}
        if specifications:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest(
                database_key=self.dbkey,
                specifications=specifications,
                indicators=indicator_objects)
            specification_response = self._compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_specifications(
                req)
            results = {**results, **specification_response.to_dict()}
        if substances:
            req = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest(
                database_key=self.dbkey,
                substances=substances,
                indicators=indicator_objects)
            substance_response = self._compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_substances(req)
            results = {**results, **substance_response.to_dict()}
        return results


class QueryBuilder:
    def __init__(self, connection):
        self._connection = connection
        self._materials = []
        self._specifications = []
        self._parts = []
        self._legislations = []
        self._substances = []

    def add_part(self,
                 part_id: str = None,
                 record_history_identity: int = None,
                 record_guid: str = None,
                 record_history_guid: str = None) -> None:
        part_reference = _PartReference(record_history_identity=record_history_identity,
                                        record_guid=record_guid,
                                        record_history_guid=record_history_guid,
                                        part_id=part_id)
        self._add_part_reference(part_reference)

    def add_specification(self,
                          specification_id: str = None,
                          record_history_identity: int = None,
                          record_guid: str = None,
                          record_history_guid: str = None) -> None:
        spec_reference = _SpecificationReference(record_history_identity=record_history_identity,
                                                 record_guid=record_guid,
                                                 record_history_guid=record_history_guid,
                                                 specification_id=specification_id)
        self._add_specification_reference(spec_reference)

    def add_material(self,
                     material_id: str = None,
                     record_history_identity: str = None,
                     record_guid: str = None,
                     record_history_guid: str = None) -> None:
        mat_reference = _MaterialReference(record_history_identity=record_history_identity,
                                           record_guid=record_guid,
                                           record_history_guid=record_history_guid,
                                           material_id=material_id)
        self._add_material_reference(mat_reference)

    def add_substance(self,
                      substance_name: str = None,
                      cas_number: str = None,
                      ec_number: str = None,
                      record_history_identity: int = None,
                      record_guid: str = None,
                      record_history_guid: str = None,
                      percentage_threshold: float = None) -> None:
        substance_reference = _SubstanceReference(record_history_identity=record_history_identity,
                                                  record_guid=record_guid,
                                                  record_history_guid=record_history_guid,
                                                  substance_name=substance_name,
                                                  cas_number=cas_number,
                                                  ec_number=ec_number)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._add_substance_reference(substance_reference)

    def from_stk(self, stk_references: List[Dict[str, str]]) -> None:
        for ref in stk_references:
            dbkey = ref['dbkey']
            if not self._connection.dbkey:
                self._connection.dbkey = dbkey
            else:
                if dbkey != self._connection.dbkey:
                    raise Exception('Wrong dbkey')
            table = ref['table']
            if table not in ['MaterialUniverse', 'Products and Parts', 'Specifications']:
                raise Exception('Unsupported table')
            guid = ref['record_guid']

            table_type = self._connection.get_table_type(table)
            if table_type == TableType.material:
                material_reference = _MaterialReference(record_guid=guid)
                self._add_material_reference(material_reference)
            elif table_type == TableType.part:
                part_reference = _PartReference(record_guid=guid)
                self._add_part_reference(part_reference)
            elif table_type == TableType.specification:
                specification_reference = _SpecificationReference(record_guid=guid)
                self._add_specification_reference(specification_reference)
            elif table_type == TableType.substance:
                substance_reference = _SubstanceReference(record_guid=guid)
                self._add_substance_reference(substance_reference)
            else:
                Exception(f"Table type {table_type} unsupported here")

    def _add_part_reference(self, part_reference: _BoMReference):
        self._parts.append(part_reference.definition)

    def _add_material_reference(self, material_reference: _BoMReference):
        self._materials.append(material_reference.definition)

    def _add_specification_reference(self, specification_reference: _BoMReference):
        self._specifications.append(specification_reference.definition)

    def _add_substance_reference(self, substance_reference: _BoMReference):
        self._substances.append(substance_reference.definition)

    def get_impacted_substances_for_legislations(self, legislations: List[str], batch_size: int = 100) -> Dict:
        return self._connection.get_impacted_substances_for_legislations(legislations,
                                                                         self._parts,
                                                                         self._specifications,
                                                                         self._materials)

    def get_compliance_for_indicators(self, indicators: List[Indicator], batch_size: int = 100) -> Dict:
        return self._connection.get_compliance_for_indicators(indicators,
                                                              self._parts,
                                                              self._specifications,
                                                              self._materials,
                                                              self._substances)
