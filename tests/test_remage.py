from __future__ import annotations

import os

import pygeomtools
import pytest

from pygeomhades import core

public_geom = os.getenv("LEGEND_METADATA", "") == ""

pytestmark = [
    pytest.mark.xfail(run=True, reason="requires a remage installation"),
    pytest.mark.needs_remage,
]


@pytest.fixture
def gdml_file(tmp_path):
    reg = core.construct(
        "V07302A",  # this works since its larger than the test detector
        "am_HS1_top_dlt",
        config={"lead_castle_idx": 1},
        public_geometry=True,
    )

    gdml_file = tmp_path / "hades-public.gdml"
    pygeomtools.write_pygeom(reg, gdml_file)

    return gdml_file


def test_overlaps(gdml_file):
    from remage import remage_run

    macro = [
        "/RMG/Geometry/RegisterDetectorsFromGDML Germanium",
        "/run/initialize",
    ]

    remage_run(macro, gdml_files=str(gdml_file), raise_on_error=True, raise_on_warning=True)
