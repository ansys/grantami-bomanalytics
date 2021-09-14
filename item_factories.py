from abc import ABC, abstractmethod
from item_definitions import (MaterialDefinition,
                              PartDefinition,
                              SpecificationDefinition,
                              SubstanceDefinition,
                              BoM1711Definition,
                              )
from item_results import (MaterialComplianceResult,
                          MaterialImpactedSubstancesResult,
                          PartComplianceResult,
                          PartImpactedSubstancesResult,
                          SpecificationComplianceResult,
                          SpecificationImpactedSubstancesResult,
                          SubstanceComplianceResult,
                          )


class RecordFactory(ABC):
    @abstractmethod
    def create_definition(self, record_history_identity=None, record_history_guid=None, record_guid=None):
        pass

    @abstractmethod
    def create_result(self, values):
        pass


class MaterialFactory(RecordFactory, ABC):
    def create_definition(self, record_history_identity=None, record_history_guid=None, record_guid=None):
        return MaterialDefinition(record_history_identity=record_history_identity,
                                  record_guid=record_guid,
                                  record_history_guid=record_history_guid)

    def create_definition_by_material_id(self, material_id):
        return MaterialDefinition(material_id=material_id)


class MaterialComplianceFactory(MaterialFactory):
    def create_result(self, values):
        return MaterialComplianceResult(results=values)


class MaterialImpactedSubstancesFactory(MaterialFactory):
    def create_result(self, values):
        return MaterialImpactedSubstancesResult(results=values)


class PartFactory(RecordFactory, ABC):
    def create_definition(self, record_history_identity=None, record_history_guid=None, record_guid=None):
        return PartDefinition(record_history_identity=record_history_identity,
                              record_guid=record_guid,
                              record_history_guid=record_history_guid)

    def create_definition_by_part_number(self, part_number):
        return PartDefinition(part_number=part_number)


class PartComplianceFactory(PartFactory):
    def create_result(self, values):
        return PartComplianceResult(results=values)


class PartImpactedSubstancesFactory(PartFactory):
    def create_result(self, values):
        return PartImpactedSubstancesResult(results=values)


class SpecificationFactory(RecordFactory, ABC):
    def create_definition(self, record_history_identity=None, record_history_guid=None, record_guid=None):
        return SpecificationDefinition(record_history_identity=record_history_identity,
                              record_guid=record_guid,
                              record_history_guid=record_history_guid)

    def create_definition_by_specification_id(self, specification_id):
        return SpecificationDefinition(specification_id=specification_id)


class SpecificationComplianceFactory(SpecificationFactory):
    def create_result(self, values):
        return SpecificationComplianceResult(results=values)


class SpecificationImpactedSubstancesFactory(SpecificationFactory):
    def create_result(self, values):
        return SpecificationImpactedSubstancesResult(results=values)


class SubstanceComplianceFactory(RecordFactory):      # TODO Re-evaluate this decision
    def create_definition(self, record_history_identity=None, record_history_guid=None, record_guid=None):
        return SubstanceDefinition(record_history_identity=record_history_identity,
                                   record_guid=record_guid,
                                   record_history_guid=record_history_guid,
                                   percentage_amount=100)

    def create_definition_by_substance_name(self, value):
        return SubstanceDefinition(substance_name=value, percentage_amount=100)

    def create_definition_by_cas_number(self, value):
        return SubstanceDefinition(cas_number=value, percentage_amount=100)

    def create_definition_by_ec_number(self, value):
        return SubstanceDefinition(ec_number=value, percentage_amount=100)

    def create_result(self, values):
        return SubstanceComplianceResult(results=values)


class BomFactory(ABC):
    def create_definition(self, bom):
        return BoM1711Definition(bom=bom)

    @abstractmethod
    def create_result(self, values):
        pass


class BomComplianceFactory(BomFactory):
    def create_result(self, values):
        return values   # TODO


class BomImpactedSubstancesFactory(BomFactory):
    def create_result(self, values):
        return values   # TODO
