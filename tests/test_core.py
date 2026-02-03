from __future__ import annotations

import os

import pygeomtools
from pyg4ometry import geant4

from pygeomhades.core import construct

public_geom = os.getenv("LEGEND_METADATA", "") == ""


def test_import():
    import pygeomhades  # noqa: F401


def test_construct():
    # test for a bege
    reg = construct(
        config={
            "hpge_name": "B00000B",
            "lead_castle_idx": 1,
            "source": "am_collimated",
            "measurement_type": "top",
        },
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)

    # test for table 2
    reg = construct(
        config={
            "hpge_name": "B00000B",
            "lead_castle_idx": 2,
            "source": "am_collimated",
            "measurement_type": "top",
        },
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)
