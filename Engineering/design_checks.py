from dataclasses import dataclass


@dataclass
class DesignCheck:
    """
    Result of a structural design check.
    """

    calculated_value: float
    allowable_value: float
    utilisation: float
    passes: bool


def check_value(
    calculated_value,
    allowable_value
):
    """
    Compare a calculated structural value
    against an allowable value.

    Utilisation = calculated / allowable

    Utilisation <= 1.0  -> PASS
    Utilisation > 1.0   -> FAIL
    """

    if allowable_value <= 0:
        raise ValueError(
            "Allowable value must be greater than zero."
        )

    utilisation = calculated_value / allowable_value

    passes = utilisation <= 1.0

    return DesignCheck(
        calculated_value=calculated_value,
        allowable_value=allowable_value,
        utilisation=utilisation,
        passes=passes
    )