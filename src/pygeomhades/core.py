from __future__ import annotations

import contextlib
import logging
from importlib import resources

import dbetto
from dbetto import TextDB
from git import GitCommandError
from legendmeta import LegendMetadata
from pyg4ometry import geant4, visualisation

from pygeomhades import dimensions as dim
from pygeomhades.create_volumes import (
    create_bottom_plate,
    create_cryostat,
    create_detector,
    create_holder,
    create_lead_castle,
    create_source,
    create_source_holder,
    create_vacuum_cavity,
    create_wrap,
)

log = logging.getLogger(__name__)

DEFAULT_DIMENSIONS = TextDB(resources.files("pygeomhades") / "configs" / "holder_wrap")

# TODO: Could the user want to remove sections of the geometry?
DEFAULT_ASSEMBLIES = {
    "vacuum_cavity",
    "bottom_plate",
    "lead_castle",
    "cryostat",
    "holder",
    "wrap",
    "detector",
    # "source",
    # "source_holder"
}


def merge_configs(ged_name: str, lmeta, config) -> dict:
    ged_diode_meta = lmeta.hardware.detectors.germanium.diodes[ged_name]
    # make sure there is an enrichment value
    if ged_diode_meta["production"]["enrichment"]["val"] is None:
        ged_diode_meta["production"]["enrichment"]["val"] = 0.9  # reasonable value
    ged_hades_config = config[ged_name]
    ged_diode_meta.update({"hades": {"dimensions": ged_hades_config}})

    return ged_diode_meta


def construct(
    assemblies: list[str] | set[str] = DEFAULT_ASSEMBLIES,
    dimensions: dict = DEFAULT_DIMENSIONS,
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

    if config is None:
        config = {"hpge_name": "V03421A", "lead_castle": 1}

    hpge_name = config["hpge_name"]
    hpge_meta = merge_configs(hpge_name, lmeta, dimensions)
    dim.update_dims(hpge_meta, config)

    reg = geant4.Registry()

    # Create the world volume
    world_material = geant4.MaterialPredefined("G4_AIR")
    world = geant4.solid.Box("world", 10, 10, 10, reg, "m")
    world_lv = geant4.LogicalVolume(world, world_material, "world_lv", reg)
    reg.setWorld(world_lv)

    if "vacuum_cavity" in assemblies:
        cavity_lv = create_vacuum_cavity(reg)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.CRYOSTAT["position_cavity_from_top"], "mm"],
            cavity_lv,
            "cavity_pv",
            world_lv,
            registry=reg,
        )

        if "wrap" in assemblies:
            wrap_lv = create_wrap(hpge_meta, from_gdml=True)
            geant4.PhysicalVolume(
                [0, 0, 0],
                [0, 0, dim.POSITIONS_FROM_CRYOSTAT["wrap"] - dim.CRYOSTAT["position_cavity_from_top"], "mm"],
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
                    dim.POSITIONS_FROM_CRYOSTAT["holder"] - dim.CRYOSTAT["position_cavity_from_top"],
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
                    (dim.POSITIONS_FROM_CRYOSTAT["detector"] - dim.CRYOSTAT["position_cavity_from_top"]),
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
            [0, 0, dim.CRYOSTAT["position_cavity_from_bottom"] + (dim.BOTTOM_PLATE["height"]) / 2, "mm"],
            plate_lv,
            "plate_pv",
            world_lv,
            registry=reg,
        )

    if "lead_castle" in assemblies:
        castle_lv = create_lead_castle(config["lead_castle"], from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.CRYOSTAT["position_cavity_from_bottom"] - (dim.LEAD_CASTLE["base_height"]) / 2, "mm"],
            castle_lv,
            "castle_pv",
            world_lv,
            registry=reg,
        )

    if "source" in assemblies:
        source_lv = create_source(from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, -dim.POSITIONS_FROM_CRYOSTAT["source"]["z"], "mm"],
            source_lv,
            "source_pv",
            world_lv,
            registry=reg,
        )

    if "source_holder" in assemblies:
        s_holder_lv = create_source_holder(from_gdml=True)
        geant4.PhysicalVolume(
            [0, 0, 0],
            [
                0,
                0,
                -(dim.POSITIONS_FROM_CRYOSTAT["source"]["z"] + dim.SOURCE_HOLDER["top_plate_height"] / 2),
                "mm",
            ],
            s_holder_lv,
            "s_holder_pv",
            world_lv,
            registry=reg,
        )

    if "cryostat" in assemblies:
        cryo_lv = create_cryostat(hpge_meta, from_gdml=True)
        geant4.PhysicalVolume([0, 0, 0], [0, 0, 0, "mm"], cryo_lv, "cryo_pv", world_lv, registry=reg)

    v = visualisation.VtkViewer()
    v.addLogicalVolume(reg.getWorldVolume())
    v.view()

    return reg
