from abc import ABC, abstractmethod
from item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    SubstanceDefinition,
    BoM1711Definition,
)
from query_results import (
    MaterialComplianceResult,
    MaterialImpactedSubstancesResult,
    PartComplianceResult,
    PartImpactedSubstancesResult,
    SpecificationComplianceResult,
    SpecificationImpactedSubstancesResult,
    SubstanceComplianceResult,
    BoMImpactedSubstancesResult,
    BoMComplianceResult,
)


class RecordFactory(ABC):
    @abstractmethod
    def create_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ):
        pass

    @abstractmethod
    def create_result(self, values):
        pass


class MaterialFactory(RecordFactory, ABC):
    def create_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> MaterialDefinition:
        return MaterialDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )

    def create_definition_by_material_id(self, material_id) -> MaterialDefinition:
        return MaterialDefinition(material_id=material_id)


class MaterialComplianceFactory(MaterialFactory):
    def create_result(self, values) -> MaterialComplianceResult:
        return MaterialComplianceResult(results=values)


class MaterialImpactedSubstancesFactory(MaterialFactory):
    def create_result(self, values) -> MaterialImpactedSubstancesResult:
        return MaterialImpactedSubstancesResult(results=values)


class PartFactory(RecordFactory, ABC):
    def create_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> PartDefinition:
        return PartDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )

    def create_definition_by_part_number(self, part_number) -> PartDefinition:
        return PartDefinition(part_number=part_number)


class PartComplianceFactory(PartFactory):
    def create_result(self, values) -> PartComplianceResult:
        return PartComplianceResult(results=values)


class PartImpactedSubstancesFactory(PartFactory):
    def create_result(self, values) -> PartImpactedSubstancesResult:
        return PartImpactedSubstancesResult(results=values)


class SpecificationFactory(RecordFactory, ABC):
    def create_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> SpecificationDefinition:
        return SpecificationDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )

    def create_definition_by_specification_id(
        self, specification_id
    ) -> SpecificationDefinition:
        return SpecificationDefinition(specification_id=specification_id)


class SpecificationComplianceFactory(SpecificationFactory):
    def create_result(self, values) -> SpecificationComplianceResult:
        return SpecificationComplianceResult(results=values)


class SpecificationImpactedSubstancesFactory(SpecificationFactory):
    def create_result(self, values) -> SpecificationImpactedSubstancesResult:
        return SpecificationImpactedSubstancesResult(results=values)


class SubstanceComplianceFactory(RecordFactory):
    def create_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> SubstanceDefinition:
        return SubstanceDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
            percentage_amount=100,
        )

    def create_definition_by_chemical_name(self, value) -> SubstanceDefinition:
        return SubstanceDefinition(chemical_name=value)

    def create_definition_by_cas_number(self, value) -> SubstanceDefinition:
        return SubstanceDefinition(cas_number=value)

    def create_definition_by_ec_number(self, value) -> SubstanceDefinition:
        return SubstanceDefinition(ec_number=value)

    def create_result(self, values) -> SubstanceComplianceResult:
        return SubstanceComplianceResult(results=values)


class BomFactory(ABC):
    def create_definition(self, bom) -> BoM1711Definition:
        return BoM1711Definition(bom=bom)

    @abstractmethod
    def create_result(self, values):
        pass


class BomComplianceFactory(BomFactory):
    def create_result(self, value) -> BoMComplianceResult:
        return BoMComplianceResult(result=value)


class BomImpactedSubstancesFactory(BomFactory):
    def create_result(self, value) -> BoMImpactedSubstancesResult:
        return BoMImpactedSubstancesResult(result=value)
