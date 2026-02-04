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
from pygeomhades import set_source_position as source_pos
from pygeomhades.create_volumes import (
    create_bottom_plate,
    create_cryostat,
    create_holder,
    create_hpge,
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

DEFAULT_ASSEMBLIES = {"hpge", "source"}


def _place_pv(
    lv: geant4.LogicalVolume,
    name: str,
    mother_lv: geant4.LogicalVolume,
    reg: geant4.registry,
    *,
    x_in_mm: float = 0,
    y_in_mm: float = 0,
    z_in_mm: float = 0,
) -> geant4.PhysicalVolume:
    """Wrapper to place the physical volume more concisely."""
    return geant4.PhysicalVolume(
        [0, 0, 0],
        [x_in_mm, y_in_mm, z_in_mm, "mm"],
        lv,
        name,
        mother_lv,
        registry=reg,
    )


def construct(
    assemblies: list[str] | set[str] = DEFAULT_ASSEMBLIES,
    extra_meta: TextDB | Path | str = DEFAULT_DIMENSIONS,
    config: str | Mapping | None = None,
    public_geometry: bool = False,
) -> geant4.Registry:
    """Construct the HADES geometry and return the registry containing the world volume.

    Parameters
    ----------
    assemblies
        A list of assemblies to construct, should be a subset of:
        - vacuum_cavity
        - bottom_plate
        - lead_castle
        - cryostat
        - holder
        - wrap
        - detector
        - source
        - source_holder

    extra_meta
        Extra metadata needed to construct the geometry (or a path to it).
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
        lead_castle: 1

    public_geometry
      if true, uses the public geometry metadata instead of the LEGEND-internal
      legend-metadata.
    """

    if not isinstance(extra_meta, TextDB):
        extra_meta = TextDB(extra_meta)

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
            "campaign": "c1",
            "measurement": "am_HS1_top_dlt",
            "run": "0001",
            "phi_position":0.0,
            "r_position": 57.5,
            "z_position": 3.0
        }

    source_type = config["measurement"][:6]
    hpge_name = config["hpge_name"]
    diode_meta = lmeta.hardware.detectors.germanium.diodes[hpge_name]
    hpge_meta = merge_configs(diode_meta, extra_meta[hpge_name])

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

    if "hpge" in assemblies:

        #create the vacuum cavity
        cavity_lv = create_vacuum_cavity(cryostat_meta, reg)
        _place_pv(cavity_lv, "cavity_pv", world_lv, reg, z_in_mm=cryostat_meta.position_cavity_from_top)

        #create the wrap
        wrap_lv = create_wrap(hpge_meta.hades.wrap.geometry, from_gdml=True)

        z_pos = hpge_meta.hades.wrap.position - cryostat_meta.position_cavity_from_top
        pv = _place_pv(wrap_lv, "wrap_pv", cavity_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        #create the holder
        holder_lv = create_holder(hpge_meta.hades.holder.geometry, hpge_meta.type, from_gdml=True)
        z_pos = hpge_meta.hades.holder.position - cryostat_meta.position_cavity_from_top

        pv = _place_pv(holder_lv, "holder_pv", cavity_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        #create the detector
        detector_lv = create_hpge(reg, hpge_meta)

        z_pos = hpge_meta.hades.detector.position - cryostat_meta.position_cavity_from_top

        pv = _place_pv(detector_lv, hpge_meta.name, cavity_lv, reg, z_in_mm=z_pos)

        #create the cryostat
        cryo_lv = create_cryostat(cryostat_meta, from_gdml=True)
        pv = _place_pv(cryo_lv, "cryo_pv", world_lv, reg)
        reg.addVolumeRecursive(pv)

    if "source" in assemblies:
        source_dims = dim.get_source_metadata(source_type)
        holder_dims = {}

        source_lv = create_source(source_type, source_dims, holder_dims, from_gdml=True)
        run, source_position, _ = source_pos.set_source_position(config)
        x_pos, y_pos, z_pos = source_position    
        #z_pos = hpge_meta.hades.source.z.position
        pv = _place_pv(source_lv, "source_pv", world_lv, reg, x_in_mm=x_pos, y_in_mm=y_pos, z_in_mm=z_pos)

        if source_type == "th_HS2":
            th_plate_lv = create_th_plate(source_dims, from_gdml=True)
            pv = _place_pv(th_plate_lv, "th_plate_pv", world_lv, reg)

    if source_type != "am_HS1":
        #add source holder
        holder_dims = {}
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
    
        #insert bottom plate and lead castle only for Static measurements
        
        plate_meta = dim.get_bottom_plate_metadata()
        plate_lv = create_bottom_plate(plate_meta, from_gdml=True)

        z_pos = cryostat_meta.position_from_bottom + plate_meta.height / 2.0
        pv = _place_pv(plate_lv, "plate_pv", world_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        table = 1 #check the single (?) measurement that wants lead castle 2
        castle_dims = dim.get_castle_dimensions(table)
        castle_lv = create_lead_castle(table, castle_dims, from_gdml=True)

        z_pos = cryostat_meta.position_from_bottom - castle_dims.base.height / 2.0
        pv = _place_pv(castle_lv, "castle_pv", world_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)


    return reg
