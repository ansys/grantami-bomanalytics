from typing import Optional
import pytest
from ansys.grantami.bomanalytics._item_results import SubstanceMerger, ImpactedSubstance
from ansys.grantami.bomanalytics._item_definitions import ReferenceType

CAS_NUMBER = "CAS"


def create_impacted_substance(amount: Optional[float] = None, threshold: Optional[float] = None) -> ImpactedSubstance:
    return ImpactedSubstance(
        reference_type=ReferenceType.CasNumber,
        reference_value=CAS_NUMBER,
        max_percentage_amount_in_material=amount,
        legislation_threshold=threshold,
    )


@pytest.mark.parametrize(
    "amount_1, amount_2, amount_result", [(1, 1, 1), (1, 2, 2), (None, 2, 2), (2, 1, 2), (2, None, 2)]
)
@pytest.mark.parametrize(
    "threshold_1, threshold_2, threshold_result", [(1, 1, 1), (1, 2, 1), (None, 2, 2), (2, 1, 1), (2, None, 2)]
)
def test_amounts(amount_1, amount_2, amount_result, threshold_1, threshold_2, threshold_result):
    merger = SubstanceMerger()
    merger.add_substance(create_impacted_substance(amount=amount_1, threshold=threshold_1))
    merger.add_substance(create_impacted_substance(amount=amount_2, threshold=threshold_2))
    assert len(merger.substances) == 1
    assert merger.substances[0].cas_number == CAS_NUMBER
    assert merger.substances[0].max_percentage_amount_in_material == amount_result
    assert merger.substances[0].legislation_threshold == threshold_result


def test_clearing_legislation_threshold():
    merger = SubstanceMerger()
    merger.add_substance(create_impacted_substance(amount=50, threshold=25))
    merger.add_substance(create_impacted_substance(amount=10, threshold=2))
    merger.clear_legislation_threshold()
    assert not any([s.legislation_threshold for s in merger.substances])
