import pytest

from ansys.grantami.bomanalytics import queries

DISTANCE = "a"
ENERGY = "b"
MASS = "c"


class TestUnitSelection:
    @pytest.mark.parametrize("mass", [MASS, None])
    @pytest.mark.parametrize("energy", [ENERGY, None])
    @pytest.mark.parametrize("distance", [DISTANCE, None])
    @pytest.mark.parametrize("query_type", [queries.BomSustainabilitySummaryQuery, queries.BomSustainabilityQuery])
    def test_units_are_set(self, query_type, mass, energy, distance):
        query = query_type()
        query.with_units(distance=distance, energy=energy, mass=mass)
        assert query._preferred_units.mass_unit == mass
        assert query._preferred_units.distance_unit == distance
        assert query._preferred_units.energy_unit == energy
