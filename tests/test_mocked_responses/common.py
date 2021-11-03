from ..common import (
    pytest,
    Union,
    List,
    Dict,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsResponse,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsResponse,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
    queries,
    indicators,
    examples_as_strings,
    requests_mock,
    check_query_manager_attributes,
    PartWithComplianceResult,
    SpecificationWithComplianceResult,
    MaterialWithComplianceResult,
    SubstanceWithComplianceResult,
    CoatingWithComplianceResult,
)


def get_mocked_response(query, result_model, connection):
    text = examples_as_strings[result_model]
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text="")
        m.post(url=requests_mock.ANY, text=text)
        response = connection.run(query)
    return response


class ObjValidator:
    def __init__(self, obj):
        self.obj = obj

    def check_reference(self, record_history_identity=None, record_guid=None):
        return (
            not self.obj.record_history_guid
            and self.obj.record_guid == record_guid
            and self.obj.record_history_identity == record_history_identity
        )

    def check_indicators(self, indicator_results):
        return all(
            self._check_indicator(name, ind, res)
            for (name, ind), res in zip(self.obj.indicators.items(), indicator_results)
        )

    @staticmethod
    def _check_indicator(name: str, indicator: indicators._Indicator, result: indicators._Flag):
        if name not in ["Indicator 1", "Indicator 2"]:
            return False
        if indicator.legislation_names != ["Mock"]:
            return False
        return indicator.flag == result


class PartValidator(ObjValidator):
    def check_reference(self, part_number=None, record_history_identity=None, record_guid=None):
        return self.obj.part_number == part_number and super().check_reference(record_history_identity, record_guid)

    def check_bom_structure(self):
        if any(
            [
                self.obj.parts is None,
                self.obj.materials is None,
                self.obj.substances is None,
                self.obj.specifications is None,
            ]
        ):
            return False
        if hasattr(self.obj, "coatings"):
            return False
        return True

    def check_empty_children(self, parts=False, materials=False, specifications=False, substances=False):
        if parts and self.obj.parts != []:
            return False
        if materials and self.obj.materials != []:
            return False
        if specifications and self.obj.specifications != []:
            return False
        if substances and self.obj.substances != []:
            return False
        return True


class SpecificationValidator(ObjValidator):
    def check_reference(self, specification_id=None, record_history_identity=None, record_guid=None):
        return self.obj.specification_id == specification_id and super().check_reference(
            record_history_identity, record_guid
        )

    def check_bom_structure(self):
        if any(
            [
                self.obj.coatings is None,
                self.obj.materials is None,
                self.obj.substances is None,
                self.obj.specifications is None,
            ]
        ):
            return False
        if hasattr(self.obj, "parts"):
            return False
        return True

    def check_empty_children(self, coatings=False, materials=False, specifications=False, substances=False):
        if coatings and self.obj.coatings != []:
            return False
        if materials and self.obj.materials != []:
            return False
        if specifications and self.obj.specifications != []:
            return False
        if substances and self.obj.substances != []:
            return False
        return True


class MaterialValidator(ObjValidator):
    def check_reference(self, material_id=None, record_history_identity=None, record_guid=None):
        return self.obj.material_id == material_id and super().check_reference(record_history_identity, record_guid)

    def check_bom_structure(self):
        if self.obj.substances is None:
            return False
        if any(
            [
                hasattr(self.obj, "parts"),
                hasattr(self.obj, "specifications"),
                hasattr(self.obj, "coatings"),
                hasattr(self.obj, "materials"),
            ]
        ):
            return False
        return True

    def check_empty_children(self, substances=False):
        if substances and self.obj.substances != []:
            return False
        return True


class CoatingValidator(ObjValidator):
    def check_bom_structure(self):
        if self.obj.substances is None:
            return False
        if any(
            [
                hasattr(self.obj, "parts"),
                hasattr(self.obj, "specifications"),
                hasattr(self.obj, "coatings"),
                hasattr(self.obj, "materials"),
            ]
        ):
            return False
        return True

    def check_empty_children(self, substances=False):
        if substances and self.obj.substances != []:
            return False
        return True


class SubstanceValidator(ObjValidator):
    def check_reference(
        self, cas_number=None, ec_number=None, chemical_name=None, record_history_identity=None, record_guid=None
    ):
        return (
            self.obj.cas_number == cas_number
            and self.obj.ec_number == ec_number
            and self.obj.chemical_name == chemical_name
            and super().check_reference(record_history_identity, record_guid)
        )

    def check_quantities(self, amount, threshold):
        return self.obj.max_percentage_amount_in_material == amount and self.obj.legislation_threshold == threshold

    def check_bom_structure(self):
        if any(
            [
                hasattr(self.obj, "parts"),
                hasattr(self.obj, "specifications"),
                hasattr(self.obj, "coatings"),
                hasattr(self.obj, "materials"),
                hasattr(self.obj, "substances"),
            ]
        ):
            return False
        return True

    def check_substance_details(self):
        return (
            (
                self.check_reference(cas_number="106-99-0", ec_number="203-450-8", chemical_name="1,3-Butadiene")
                and self.check_quantities(None, 0.1)
            )
            or (
                self.check_reference(
                    cas_number="128-37-0", ec_number="204-881-4", chemical_name="Butylated hydroxytoluene [BAN:NF]"
                )
                and self.check_quantities(None, 0.1)
            )
            or (
                self.check_reference(cas_number="119-61-9", ec_number="204-337-6", chemical_name="Benzophenone")
                and self.check_quantities(1.0, 0.1)
            )
            or (
                self.check_reference(
                    cas_number="131-56-6", ec_number="205-029-4", chemical_name="2,4-Dihydroxybenzophenon"
                )
                and self.check_quantities(1.0, 0.1)
            )
        )
