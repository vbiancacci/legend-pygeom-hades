from __future__ import annotations

from importlib import resources

import pyg4ometry

from pygeomhades.metadata import PublicMetadataProxy
from pygeomhades.utils import merge_configs, parse_measurement, read_gdml_with_replacements


def test_merge_config():
    meta = PublicMetadataProxy()

    hpge_meta = merge_configs(meta.hardware.detectors.germanium.diodes["V07302A"], {"dimensions": 1})

    assert hpge_meta.hades.dimensions == 1
    assert hpge_meta.production.enrichment.val is not None


def test_read_gdml_with_replacements():
    dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "wrap_dummy.gdml"
    replacements = {
        "wrap_outer_height_in_mm": 100,
        "wrap_outer_radius_in_mm": 99,
        "wrap_inner_radius_in_mm": 98,
        "wrap_top_thickness_in_mm": 1,
    }

    lv = read_gdml_with_replacements(dummy_gdml_path, replacements)

    assert isinstance(lv, pyg4ometry.geant4.LogicalVolume)


def test_parse_measurement_basic():
    out = parse_measurement("cs_HS2_bottom_foo")

    assert out.source == "cs"
    assert out.holder == "HS2"
    assert out.position == "bottom"
    assert out.id == "foo"

    out = parse_measurement("am_HS1_top_dlt")

    assert out.source == "am_collimated"
    assert out.holder == "HS1"
    assert out.position == "top"
    assert out.id == "dlt"

    out = parse_measurement("am_HS2_top_dlt")

    assert out.source == "am"  # no renaming
    assert out.holder == "HS2"
