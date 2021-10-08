from ..common import (
    pytest,
    Union,
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


def check_substance(substance):
    return (
        _check_specific_substance(substance, "106-99-0", "203-450-8", "1,3-Butadiene", None, 0.1)
        or _check_specific_substance(substance, "128-37-0", "204-881-4", "Butylated hydroxytoluene [BAN:NF]", None, 0.1)
        or _check_specific_substance(substance, "119-61-9", "204-337-6", "Benzophenone", 1.0, 0.1)
        or _check_specific_substance(substance, "131-56-6", "205-029-4", "2,4-Dihydroxybenzophenon", 1.0, 0.1)
    )


def _check_specific_substance(
    substance, cas: str, ec: str, chemical_name: str, amount: Union[float, None], threshold: float
):
    return (
        substance.cas_number == cas
        and substance.ec_number == ec
        and substance.chemical_name == chemical_name
        and substance.max_percentage_amount_in_material == amount
        and substance.legislation_threshold == threshold
    )


def check_indicator(name: str, indicator: indicators._Indicator, impacted: bool = True):
    if name not in ["Indicator 1", "Indicator 2"]:
        return False
    if indicator.legislation_names != ["Mock"]:
        return False
    if impacted:
        if indicator.name == "Indicator 1" and indicator.flag.name == "WatchListAboveThreshold":
            return True
        if indicator.name == "Indicator 2" and indicator.flag.name == "RohsAboveThreshold":
            return True
    else:
        if indicator.name == "Indicator 1" and indicator.flag.name == "WatchListNotImpacted":
            return True
        if indicator.name == "Indicator 2" and indicator.flag.name == "RohsNotImpacted":
            return True
    return False


def check_part_attributes(part: PartWithComplianceResult):
    if part.parts is None or part.materials is None or part.substances is None or part.specifications is None:
        return False
    if hasattr(part, "coatings"):
        return False
    return True


def check_specification_attributes(specification: SpecificationWithComplianceResult):
    if (
        specification.coatings is None
        or specification.materials is None
        or specification.substances is None
        or specification.specifications is None
    ):
        return False
    if hasattr(specification, "parts"):
        return False
    return True


def check_material_attributes(material: MaterialWithComplianceResult):
    if material.substances is None:
        return False
    if (
        hasattr(material, "parts")
        or hasattr(material, "coatings")
        or hasattr(material, "materials")
        or hasattr(material, "specifications")
    ):
        return False
    return True


def check_coating_attributes(coating: CoatingWithComplianceResult):
    if coating.substances is None:
        return False
    if (
        hasattr(coating, "parts")
        or hasattr(coating, "coatings")
        or hasattr(coating, "materials")
        or hasattr(coating, "specifications")
    ):
        return False
    return True


def check_substance_attributes(substance: SubstanceWithComplianceResult):
    if (
        hasattr(substance, "parts")
        or hasattr(substance, "coatings")
        or hasattr(substance, "materials")
        or hasattr(substance, "specifications")
        or hasattr(substance, "substances")
    ):
        return False
    return True
