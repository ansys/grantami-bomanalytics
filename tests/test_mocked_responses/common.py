import requests_mock

from ansys.grantami.bomanalytics import indicators, queries

from ..inputs import examples_as_strings


class BaseMockTester:
    mock_key: str
    query: queries._BaseQueryBuilder

    def get_mocked_response(self, connection, response=None):
        if response:
            text = response
        else:
            text = examples_as_strings[self.mock_key]
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text="")
            m.post(url=requests_mock.ANY, text=text)
            response = connection.run(self.query)
        return response


class ObjValidator:
    """Base class to validate a compliance result object."""

    def __init__(self, obj):
        self.obj = obj

    def check_reference(self, record_history_identity=None, record_guid=None):
        """Validate that only the specified references are populated, and all others are None.

        Currently only implements 'record_history_identity' and 'record_guid', because these are the only ones used
        in the example responses.
        """

        return (
            not self.obj.record_history_guid
            or (self.obj.record_guid == record_guid and record_guid is not None)
            or (self.obj.record_history_identity == record_history_identity and record_history_identity is not None)
        )

    def check_indicators(self, indicator_results):
        """Validate that the compliance results on the object are the same as those passed into this method."""

        return all(
            self._check_indicator(name, ind, res)
            for (name, ind), res in zip(self.obj.indicators.items(), indicator_results)
        )

    @staticmethod
    def _check_indicator(name: str, indicator: indicators._Indicator, result: indicators._Flag):
        """Check an individual indicator result against its expected value.

        Also checks that the indicator name and legislation name are certain hard-coded expected values. This might
        need to become more general in future.
        """

        if name not in ["Indicator 1", "Indicator 2"]:
            return False
        if indicator.legislation_ids != ["Mock"]:
            return False
        return indicator.flag == result


class PartValidator(ObjValidator):
    def check_reference(self, part_number=None, record_history_identity=None, record_guid=None):
        """Extend base implementation to support part_number for parts."""

        return self.obj.part_number == part_number and super().check_reference(record_history_identity, record_guid)

    def check_bom_structure(self):
        """Validate that the part compliance result has the expected properties for child bom items.

        First check that expected attributes exist. They can be empty lists, but cannot be None. If they don't exist,
        the Exception will trigger a failed test directly.

        Then check that unexpected attributes do not exist. If they do, return False.
        """

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
        """Validate that the specified child types exist for this object."""

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
        """Extend base implementation to support specification_id for specs."""

        return self.obj.specification_id == specification_id and super().check_reference(
            record_history_identity, record_guid
        )

    def check_bom_structure(self):
        """Validate that the part compliance result has the expected properties for child bom items.

        First check that expected attributes exist. They can be empty lists, but cannot be None. If they don't exist,
        the Exception will trigger a failed test directly.

        Then check that unexpected attributes do not exist. If they do, return False.
        """

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
        """Validate that the specified child types exist for this object."""

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
        """Extend base implementation to support material_id for materials."""

        return self.obj.material_id == material_id and super().check_reference(record_history_identity, record_guid)

    def check_bom_structure(self):
        """Validate that the part compliance result has the expected properties for child bom items.

        First check that expected attributes exist. They can be empty lists, but cannot be None. If they don't exist,
        the Exception will trigger a failed test directly.

        Then check that unexpected attributes do not exist. If they do, return False.
        """

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
        """Validate that the specified child types exist for this object."""

        if substances and self.obj.substances != []:
            return False
        return True


class CoatingValidator(ObjValidator):
    def check_bom_structure(self):
        """Validate that the part compliance result has the expected properties for child bom items.

        First check that expected attributes exist. They can be empty lists, but cannot be None. If they don't exist,
        the Exception will trigger a failed test directly.

        Then check that unexpected attributes do not exist. If they do, return False.
        """

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
        """Validate that the specified child types exist for this object."""

        if substances and self.obj.substances != []:
            return False
        return True


class SubstanceValidator(ObjValidator):
    def check_reference(
        self, cas_number=None, ec_number=None, chemical_name=None, record_history_identity=None, record_guid=None
    ):
        """Extend base implementation to support cas_number, ec_number, and chemical_name for substances."""

        return (
            (self.obj.cas_number == cas_number and cas_number is not None)
            or (self.obj.ec_number == ec_number and ec_number is not None)
            or (self.obj.chemical_name == chemical_name and chemical_name is not None)
            or super().check_reference(record_history_identity, record_guid)
        )

    def check_quantities(self, amount, threshold):
        """Check the quantities associated with a substance are correct."""
        return self.obj.max_percentage_amount_in_material == amount and self.obj.legislation_threshold == threshold

    def check_bom_structure(self):
        """Validate that the part compliance result has the expected properties for child bom items.

        A substance is always a leaf node, so it shouldn't have any children.
        """

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
        """There are only 4 distinct substances in the example responses. This method checks that the substance is
        one of those 4 substances."""

        assert (
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
