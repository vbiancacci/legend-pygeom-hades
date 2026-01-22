from __future__ import annotations

import os

from pygeomhades.core import construct

public_geom = os.getenv("LEGEND_METADATA", "") == ""


def test_import():
    import pygeomhades  # noqa: F401


def test_construct():
    assert construct(public_geometry=True)
