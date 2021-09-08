from ansys.granta import bomanalytics
from ansys.granta.auth_common import AuthenticatedApiClient
from typing import Union, List, Dict
from abc import ABC, abstractmethod


class BoMReference:
    mi_record_history_identity = "MiRecordHistoryIdentity"
    mi_record_guid = "MiRecordGuid"
    mi_record_history_guid = "MiRecordHistoryGuid"

    def __init__(self, reference_type: str, reference_value: Union[str, int]):
        self.reference_type = reference_type
        self.reference_value = reference_value

    @classmethod
    def by_record_history_identity(cls, record_history_identity: int):
        new = cls(cls.mi_record_history_identity, record_history_identity)
        return new

    @classmethod
    def by_record_guid(cls, record_guid: str):
        new = cls(cls.mi_record_guid, record_guid)
        return new

    @classmethod
    def by_record_history_guid(cls, record_history_guid: str):
        new = cls(cls.mi_record_history_guid, record_history_guid)
        return new


class AbstractBoMReferenceBuilder(ABC):
    item_type = None

    def __init__(self, query):
        self._query = query

    def by_record_history_identity(self, value: int):
        new = BoMReference.by_record_history_identity(value)
        self._query.add_item_from_dict(self.__class__.item_type, new)

    def by_record_guid(self, value: str):
        new = BoMReference.by_record_guid(value)
        self._query.add_item_from_dict(self.__class__.item_type, new)

    def by_record_history_guid(self, value: str):
        new = BoMReference.by_record_history_guid(value)
        self._query.add_item_from_dict(self.__class__.item_type, new)


class MaterialReferenceBuilder(AbstractBoMReferenceBuilder):
    item_type = 'material'

    def by_material_id(self, material_id: str):
        new = BoMReference("MaterialId", material_id)
        self._query.add_material_from_dict(new)


class SpecificationReferenceBuilder(AbstractBoMReferenceBuilder):
    item_type = 'specification'

    def by_specification_id(self, specification_id: str):
        new = BoMReference("SpecificationId", specification_id)
        self._query.add_specification_from_dict(new)


class PartReferenceBuilder(AbstractBoMReferenceBuilder):
    item_type = 'part'

    def by_part_id(self, part_id: str):
        new = BoMReference("PartId", part_id)
        self._query.add_part_from_dict(new)


class AsyncConnection:
    def __init__(self, url, dbkey):
        # Create a generic AuthenticatedApiClient and initialize with the relevant models
        self._client = AuthenticatedApiClient.with_credentials(servicelayer_url=url,
                                                   username='***REMOVED***', password='***REMOVED***')
        self._client.setup_client(bomanalytics.models)

        self.documentation_api = bomanalytics.DocumentationApi(self._client)
        self.compliance_api = bomanalytics.ComplianceApi(self._client)
        self.impacted_substances_api = bomanalytics.ImpactedSubstancesApi(self._client)
        self.materials = []
        self.specifications = []
        self.parts = []
        self._dbkey = dbkey

    def get_yaml(self):
        return self.documentation_api.get_miservicelayer_bom_analytics_v1svc_yaml()

    def get_impacted_substances_for_legislations(self, legislations):
        results = {}

        if self.materials:
            material_request = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest
            req = material_request(database_key=self._dbkey, materials=self.materials, legislation_names=legislations)
            subs = self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials(req)
            results = {**results, **subs.to_dict()}

        if self.specifications:
            spec_request = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest
            req = spec_request(database_key=self._dbkey, specifications=self.specifications, legislation_names=legislations)
            subs = self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications(req)
            results = {**results, **subs.to_dict()}

        if self.parts:
            part_request = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest
            req = part_request(database_key=self._dbkey, parts=self.parts, legislation_names=legislations)
            subs = self.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts(req)
            results = {**results, **subs.to_dict()}

        return results

    def get_compliance(self):
        pass


class QueryBuilder:
    def __init__(self, url, dbkey):
        self._query = AsyncConnection(url, dbkey)
        self.add_material = MaterialReferenceBuilder(self)
        self.add_specification = SpecificationReferenceBuilder(self)
        self.add_part = PartReferenceBuilder(self)

    def add_item_from_dict(self, item_type, value):
        if item_type == 'material':
            self.add_material_from_dict(value)
        elif item_type == 'part':
            self.add_part_from_dict(value)
        elif item_type == 'specification':
            self.add_specification_from_dict(value)

    def add_material_from_dict(self, material: BoMReference):
        material_ref = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference(
            reference_type=material.reference_type,
            reference_value=material.reference_value)
        self._query.materials.append(material_ref)

    def add_specification_from_dict(self, specification: BoMReference):
        spec_ref = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference(
            reference_type=specification.reference_type,
            reference_value=specification.reference_value)
        self._query.specifications.append(spec_ref)

    def add_part_from_dict(self, part: BoMReference):
        part_ref = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonPartReference(
            reference_type=part.reference_type,
            reference_value=part.reference_value)
        self._query.parts.append(part_ref)

    def get_impacted_substances_for_legislations(self, legislations):
        return self._query.get_impacted_substances_for_legislations(legislations)
