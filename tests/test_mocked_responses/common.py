from typing import Union


def check_substance(substance):
    return (
        _check_substance(substance, "106-99-0", "203-450-8", "1,3-Butadiene", None, 0.1)
        or _check_substance(substance, "128-37-0", "204-881-4", "Butylated hydroxytoluene [BAN:NF]", None, 0.1)
        or _check_substance(substance, "119-61-9", "204-337-6", "Benzophenone", 1.0, 0.1)
        or _check_substance(substance, "131-56-6", "205-029-4", "2,4-Dihydroxybenzophenon", 1.0, 0.1)
    )


def _check_substance(substance, cas: str, ec: str, chemical_name: str, amount: Union[float, None], threshold: float):
    return (
        substance.cas_number == cas
        and substance.ec_number == ec
        and substance.chemical_name == chemical_name
        and substance.max_percentage_amount_in_material == amount
        and substance.legislation_threshold == threshold
    )


def check_indicator(name: str, indicator):
    if name not in ["Indicator 1", "Indicator 2"]:
        return False
    if indicator.legislation_names != ["Mock"]:
        return False
    if indicator.name == "Indicator 1" and indicator.flag.name == "WatchListAboveThreshold":
        return True
    if indicator.name == "Indicator 2" and indicator.flag.name == "RohsAboveThreshold":
        return True
    return False
