from __future__ import annotations

import contextlib
import logging
from collections.abc import Mapping
from importlib import resources
from pathlib import Path

import dbetto
from dbetto import TextDB
from git import GitCommandError
from legendmeta import LegendMetadata
from pyg4ometry import geant4

from pygeomhades import dimensions as dim
from pygeomhades.create_volumes import (
    create_bottom_plate,
    create_cryostat,
    create_detector,
    create_holder,
    create_lead_castle,
    create_source,
    create_source_holder,
    create_th_plate,
    create_vacuum_cavity,
    create_wrap,
)
from pygeomhades.metadata import PublicMetadataProxy
from pygeomhades.utils import merge_configs

log = logging.getLogger(__name__)

DEFAULT_DIMENSIONS = TextDB(resources.files("pygeomhades") / "configs" / "holder_wrap")

DEFAULT_ASSEMBLIES = {
    "vacuum_cavity",
    # "bottom_plate",
    # "lead_castle",
    # "cryostat",
    # "holder",
    # "wrap",
    "detector",
    # "source",
    # "source_holder",
}


def construct(
    assemblies: list[str] | set[str] = DEFAULT_ASSEMBLIES,
    dimensions: TextDB | Path | str = DEFAULT_DIMENSIONS,
    config: str | Mapping | None = None,
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

    if not isinstance(dimensions, TextDB):
        dimensions = TextDB(dimensions)

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
        lmeta = PublicMetadataProxy()

    if config is None or config == {}:
        config = {
            "hpge_name": "V07302A",
            "lead_castle": 1,
            "source": "am_collimated",
            "measurement_type": "top",
        }

    hpge_name = config["hpge_name"]
    diode_meta = lmeta.hardware.detectors.germanium.diodes[hpge_name]
    hpge_meta = merge_configs(diode_meta, {"dimensions": dimensions[hpge_name]})

    dim.update_dims(hpge_meta, config)

    reg = geant4.Registry()

    # Create the world volume
    world_material = geant4.MaterialPredefined("G4_AIR")
    world = geant4.solid.Box("world", 10, 10, 10, reg, "m")
    world_lv = geant4.LogicalVolume(world, world_material, "world_lv", reg)
    reg.setWorld(world_lv)

    # extract the metadata on the cryostat
    cryostat_meta = dim.get_cryostat_metadata(
        hpge_meta.type, hpge_meta.production.order, hpge_meta.production.slice
    )

    if "vacuum_cavity" in assemblies:
        cavity_lv = create_vacuum_cavity(cryostat_meta, reg)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, cryostat_meta.position_cavity_from_top, "mm"],
            cavity_lv,
            "cavity_pv",
            world_lv,
            registry=reg,
        )

        if "wrap" in assemblies:
            wrap_lv = create_wrap(hpge_meta, from_gdml=True)
            geant4.PhysicalVolume(
                [0, 0, 0],
                [0, 0, dim.positions_from_cryostat["wrap"] - dim.cryostat["position_cavity_from_top"], "mm"],
                wrap_lv,
                "wrap_pv",
                cavity_lv,
                registry=reg,
            )

        if "holder" in assemblies:
            holder_lv = create_holder(hpge_meta, from_gdml=True)
            geant4.PhysicalVolume(
                [0, 0, 0],
                [
                    0,
                    0,
                    dim.positions_from_cryostat["holder"] - dim.cryostat["position_cavity_from_top"],
                    "mm",
                ],
                holder_lv,
                "holder_pv",
                cavity_lv,
                registry=reg,
            )

        if "detector" in assemblies:
            detector_lv = create_detector(reg, hpge_meta)
            geant4.PhysicalVolume(
                [0, 0, 0],
                [
                    0,
                    0,
                    (dim.positions_from_cryostat["detector"] - dim.cryostat["position_cavity_from_top"]),
                    "mm",
                ],
                detector_lv,
                "hpge_pv",
                cavity_lv,
                registry=reg,
            )

    if "bottom_plate" in assemblies:
        plate_lv = create_bottom_plate(from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.cryostat["position_from_bottom"] + (dim.bottom_plate["height"]) / 2, "mm"],
            plate_lv,
            "plate_pv",
            world_lv,
            registry=reg,
        )

    if "lead_castle" in assemblies:
        castle_lv = create_lead_castle(config["lead_castle"], from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.cryostat["position_from_bottom"] - (dim.lead_castle["base_height"]) / 2, "mm"],
            castle_lv,
            "castle_pv",
            world_lv,
            registry=reg,
        )

    if "source" in assemblies:
        source_lv = create_source(config, from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, -dim.positions_from_cryostat["source"]["z"], "mm"],
            source_lv,
            "source_pv",
            world_lv,
            registry=reg,
        )

        if config["source"] == "tl":
            th_plate_lv = create_th_plate(from_gdml=True)
            geant4.PhysicalVolume(
                [0, 0, 0],
                [0, 0, 0, "mm"],
                th_plate_lv,
                "th_plate_pv",
                world_lv,
                registry=reg,
            )

    if "source_holder" in assemblies:
        s_holder_lv = create_source_holder(config, from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [
                0,
                0,
                -(
                    dim.positions_from_cryostat["source"]["z"]
                    + dim.source_holder["top"]["top_plate_height"] / 2
                ),  # TODO: this will break so we need to change it
                "mm",
            ],
            s_holder_lv,
            "s_holder_pv",
            world_lv,
            registry=reg,
        )

    if "cryostat" in assemblies:
        cryo_lv = create_cryostat(from_gdml=True)
        geant4.PhysicalVolume([0, 0, 0], [0, 0, 0, "mm"], cryo_lv, "cryo_pv", world_lv, registry=reg)

    return reg
