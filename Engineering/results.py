from dataclasses import dataclass
import numpy as np


@dataclass
class BeamUDLResult:
    """
    Stores the results of a beam subjected to a
    uniformly distributed load.

    Units:
        distributed_load       -> N/m
        total_load            -> N
        reactions             -> N
        bending moment        -> Nm
        stress                -> Pa
        second moment         -> m4
        section modulus       -> m3
        deflection            -> m

    Deflection components:
    - bending_deflection: Euler-Bernoulli bending contribution
    - shear_deflection: Timoshenko shear contribution
    - max_deflection: total maximum deflection
    - shear_contribution: percentage of total deflection
      attributable to shear
    """

    distributed_load: float
    total_load: float

    left_reaction: float
    right_reaction: float

    max_bending_moment: float
    bending_stress: float

    second_moment_of_area: float
    section_modulus: float

    bending_deflection: float
    shear_deflection: float
    max_deflection: float
    shear_contribution: float

    x: np.ndarray
    shear: np.ndarray
    moment: np.ndarray
    deflection: np.ndarray


@dataclass
class PanelUDLResult:
    """
    Stores the results of a panel strip subjected
    to a uniformly distributed area load.
    """

    tributary_width: float
    section_width: float

    area_load: float
    distributed_load: float

    total_load: float

    left_reaction: float
    right_reaction: float

    max_bending_moment: float
    bending_stress: float

    second_moment_of_area: float
    section_modulus: float

    bending_deflection: float
    shear_deflection: float
    max_deflection: float
    shear_contribution: float

    x: np.ndarray
    shear: np.ndarray
    moment: np.ndarray
    deflection: np.ndarray


@dataclass
class BeamPointLoadResult:
    """
    Stores the results of a beam subjected to a
    central point load.

    Currently uses Euler-Bernoulli bending theory.
    """

    left_reaction: float
    right_reaction: float

    max_bending_moment: float
    bending_stress: float

    second_moment_of_area: float
    section_modulus: float

    max_deflection: float