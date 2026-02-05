from __future__ import annotations

import os

import pygeomtools
<<<<<<< HEAD
=======
import pytest
>>>>>>> upstream/main
from pyg4ometry import geant4

from pygeomhades.core import construct

public_geom = os.getenv("LEGEND_METADATA", "") == ""


def test_import():
    import pygeomhades  # noqa: F401


def test_construct():
<<<<<<< HEAD
    reg = construct(public_geometry=True)
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)

    # test for a bege
    reg = construct(
        config={
            "hpge_name": "B00000B",
            "lead_castle": 1,
            "source": "am_collimated",
            "measurement_type": "top",
        },
=======
    # test for a bege
    reg = construct(
        "B00000B",
        "am_HS1_top_dlt",
        config={"lead_castle_idx": 1},
>>>>>>> upstream/main
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)

    # test for table 2
    reg = construct(
<<<<<<< HEAD
        config={
            "hpge_name": "B00000B",
            "lead_castle": 2,
            "source": "am_collimated",
            "measurement_type": "top",
        },
=======
        "B00000B",
        "am_HS1_top_dlt",
        config={"lead_castle_idx": 2},
>>>>>>> upstream/main
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)
<<<<<<< HEAD
=======

    with pytest.raises(NotImplementedError):
        # test for source assembly (not yet verified)
        _ = construct(
            "B00000B",
            "am_HS1_top_dlt",
            config={"lead_castle_idx": 1},
            assemblies=["hpge", "lead_castle", "source"],
            public_geometry=True,
            construct_unverified=False,
        )
>>>>>>> upstream/main
