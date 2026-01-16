from __future__ import annotations

import contextlib
import logging

import dbetto
from git import GitCommandError
from legendmeta import LegendMetadata
from pyg4ometry import geant4

from .place_volumes import (
    place_bottom_plate,
    place_cryostat,
    place_detector,
    place_holder,
    place_lead_castle,
    place_source,
    place_source_holder,
    place_vacuum_cavity,
    place_wrap,
)

log = logging.getLogger(__name__)


# TODO: Could the user want to remove sections of the geometry?
DEFAULT_ASSEMBLIES = {
    "detector",
    "wrap",
    "holder",
    "bottom_plate",
    "lead_castle",
    "source",
    "source_holder",
    "cryostat",
}


def construct(
    assemblies: list[str] | set[str] = DEFAULT_ASSEMBLIES,
    config: str | dict | None = None,
    public_geometry: bool = False,
) -> geant4.Registry:
    """Construct the HADES geometry and return the registry containing the world volume.

    Parameters
    ----------
    config
      configuration dictionary (or file containing it) defining relevant
      parameters of the geometry.

      .. code-block:: yaml

        detector: V07302A
        measurement: am_HS1_top_dlt
        source_position:
          phi_in_deg: 0.0
          r_in_mm: 86.0
          z_in_mm: 3.0
    public_geometry
      if true, uses the public geometry metadata instead of the LEGEND-internal
      legend-metadata.
    """

    if isinstance(config, str):
        config = dbetto.utils.load_dict(config)

    lmeta = None
    if not public_geometry:
        with contextlib.suppress(GitCommandError):
            lmeta = LegendMetadata(lazy=True)
    # require user action to construct a testdata-only geometry (i.e. to avoid accidental creation of "wrong"
    # geometries by LEGEND members).
    if lmeta is None and not public_geometry:
        msg = "cannot construct geometry from public testdata only, if not explicitly instructed"
        raise RuntimeError(msg)
    if lmeta is None:
        log.warning("CONSTRUCTING GEOMETRY FROM PUBLIC DATA ONLY")
        # TODO: use this public metadata proxy
        # dummy_geom = PublicMetadataProxy()

    config = config if config is not None else {}

    reg = geant4.Registry()

    # Create the world volume
    world_material = geant4.MaterialPredefined("G4_AIR")
    world = geant4.solid.Box("world", 10, 10, 10, reg, "m")
    world_lv = geant4.LogicalVolume(world, world_material, "world_lv", reg)
    reg.setWorld(world_lv)

    # create vacuum cavity
    cavity_lv = place_vacuum_cavity(reg, world_lv)

    if "detector" in assemblies:
        detector_pv = place_detector(reg, world_lv, from_gdml=True)
        reg.addVolumeRecursive(detector_pv)

    if "wrap" in assemblies:
        wrap_pv = place_wrap(reg, cavity_lv, from_gdml=True)
        reg.addVolumeRecursive(wrap_pv)

    if "holder" in assemblies:
        holder_pv = place_holder(reg, cavity_lv, from_gdml=True)
        reg.addVolumeRecursive(holder_pv)

    if "bottom_plate" in assemblies:
        plate_pv = place_bottom_plate(reg, world_lv, from_gdml=True)
        reg.addVolumeRecursive(plate_pv)

    if "lead_castle" in assemblies:
        castle_pv = place_lead_castle(reg, world_lv, from_gdml=True)
        reg.addVolumeRecursive(castle_pv)

    if "source" in assemblies:
        source_pv = place_source(reg, world_lv, from_gdml=True)
        reg.addVolumeRecursive(source_pv)

    if "source_holder" in assemblies:
        s_holder_pv = place_source_holder(reg, world_lv, from_gdml=True)
        reg.addVolumeRecursive(s_holder_pv)

    if "cryostat" in assemblies:
        cryo_pv = place_cryostat(reg, world_lv, from_gdml=True)
        reg.addVolumeRecursive(cryo_pv)

    # visualize(reg)
    # generate_detector_macro(reg, "pv_reg.mac")
    # write_pygeom(reg, "simple_teststand.gdml")

    return reg
