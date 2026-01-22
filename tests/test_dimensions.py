from __future__ import annotations

from dbetto import AttrsDict

from pygeomhades.dimensions import get_cryostat_metadata


def test_cryostat_meta():
    assert isinstance(get_cryostat_metadata("bege", 0, "A"), AttrsDict)

    assert set(get_cryostat_metadata("bege", 0, "A").keys()) == {
        "width",
        "height",
        "thickness",
        "position_cavity_from_top",
        "position_cavity_from_bottom",
        "position_from_bottom",
    }
