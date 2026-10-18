from enum import Enum


class SupportCondition(Enum):
    """
    Supported structural boundary conditions.
    """

    SIMPLY_SUPPORTED = "simply_supported"

    FIXED_FIXED = "fixed_fixed"