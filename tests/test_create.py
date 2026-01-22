from __future__ import annotations

from dbetto import AttrsDict
from pyg4ometry import geant4

from pygeomhades.create_volumes import create_vacuum_cavity


def test_create_cavity():
    cryostat = AttrsDict(
        {
            "width": 200,
            "thickness": 1,
            "height": 200,
            "position_cavity_from_top": 1,
            "position_cavity_from_bottom": 1,
        }
    )

    reg = geant4.Registry()
    lv = create_vacuum_cavity(cryostat, reg)
    assert isinstance(lv, geant4.LogicalVolume)


def test_create_wrap():
    pass


def test_create_holder():
    pass
