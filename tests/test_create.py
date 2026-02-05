from __future__ import annotations

import pytest
from dbetto import AttrsDict
from pyg4ometry import geant4

from pygeomhades.create_volumes import create_holder, create_th_plate, create_vacuum_cavity, create_wrap


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
    wrap_metadata = AttrsDict(
        {
            "outer": {
                "height_in_mm": 100,
                "radius_in_mm": 50,
            },
            "inner": {
                "height_in_mm": 99,
                "radius_in_mm": 49,
            },
        }
    )

    wrap_lv = create_wrap(wrap_metadata, from_gdml=True)

    assert wrap_lv is not None
    assert isinstance(wrap_lv, geant4.LogicalVolume)

    with pytest.raises(NotImplementedError):
        _ = create_wrap(wrap_metadata, from_gdml=False)


def test_create_holder():
    holder = AttrsDict(
        {
            "cylinder": {
                "inner": {
                    "height_in_mm": 100,
                    "radius_in_mm": 100,
                },
                "outer": {
                    "height_in_mm": 104,
                    "radius_in_mm": 104,
                },
            },
            "bottom_cyl": {
                "inner": {
                    "height_in_mm": 100,
                    "radius_in_mm": 100,
                },
                "outer": {
                    "height_in_mm": 104,
                    "radius_in_mm": 104,
                },
            },
            "rings": {
                "position_top_ring_in_mm": 20,
                "position_bottom_ring_in_mm": 30,
                "radius_in_mm": 150,
                "height_in_mm": 10,
            },
            "edge": {
                "height_in_mm": 1000,
            },
        }
    )

    # test with bege
    lv = create_holder(holder, "bege", from_gdml=True)
    assert isinstance(lv, geant4.LogicalVolume)

    lv = create_holder(holder, "icpc", from_gdml=True)
    assert isinstance(lv, geant4.LogicalVolume)

    with pytest.raises(NotImplementedError):
        _ = create_holder(holder, "bege", from_gdml=False)


def test_create_th_plate():
    source_dims = AttrsDict({"plates": {"height": 10.0, "width": 50.0, "cavity_width": 5.0}})

    th_plate_lv = create_th_plate(source_dims, from_gdml=True)

    assert isinstance(th_plate_lv, geant4.LogicalVolume)

    with pytest.raises(NotImplementedError):
        _ = create_th_plate(source_dims, from_gdml=False)
