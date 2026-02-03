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
from pygeomhpges import make_hpge

from pygeomhades import dimensions as dim
from pygeomhades.create_volumes import (
    create_bottom_plate,
    create_cryostat,
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


DEFAULT_ASSEMBLIES = {"hpge", "lead_castle"}


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
    config: str | Mapping,
    assemblies: list[str] | set[str] = DEFAULT_ASSEMBLIES,
    extra_meta: TextDB | Path | str | None = None,
    public_geometry: bool = False,
    construct_unverified: bool = False,
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
        lead_castle_idx: 1

    assemblies
        A list of assemblies to construct, should be a subset of:
        - hpge: the detector, cryostat, holder and wrap.
        - lead_castle: the shielding and bottom plate.
        - source: the source and its holder.

    extra_meta
        Extra metadata needed to construct the geometry (or a path to it). If
        `None` then this is taken as `pygeomhades/configs/holder_wrap`.
    public_geometry
      if true, uses the public geometry metadata instead of the LEGEND-internal
      legend-metadata.
    construct_unverified
        If true, allows construction of unverified assemblies such as the source assembly.
        Default is False.
    """

    if extra_meta is None:
        extra_meta = TextDB(resources.files("pygeomhades") / "configs" / "holder_wrap")
    elif not isinstance(extra_meta, TextDB):
        extra_meta = TextDB(extra_meta)

    if isinstance(config, str):
        config = dbetto.utils.load_dict(config)

    config = dbetto.AttrsDict(config)

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

    if config == {}:
        msg = "config cannot be empty"
        raise ValueError(msg)

    hpge_name = config.hpge_name
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

    cavity_lv = create_vacuum_cavity(cryostat_meta, reg)
    _place_pv(cavity_lv, "cavity_pv", world_lv, reg, z_in_mm=cryostat_meta.position_cavity_from_top)

    if "hpge" in assemblies:
        # construct the mylar wrap
        wrap_lv = create_wrap(hpge_meta.hades.wrap.geometry, from_gdml=True)

        z_pos = hpge_meta.hades.wrap.position - cryostat_meta.position_cavity_from_top
        pv = _place_pv(wrap_lv, "wrap_pv", cavity_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        # construct the holder
        holder_lv = create_holder(hpge_meta.hades.holder.geometry, hpge_meta.type, from_gdml=True)
        z_pos = hpge_meta.hades.holder.position - cryostat_meta.position_cavity_from_top

        pv = _place_pv(holder_lv, "holder_pv", cavity_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        # construct the hpge
        detector_lv = make_hpge(hpge_meta, name=hpge_meta.name, registry=reg)

        z_pos = hpge_meta.hades.detector.position - cryostat_meta.position_cavity_from_top
        pv = _place_pv(detector_lv, hpge_meta.name, cavity_lv, reg, z_in_mm=z_pos)

        # construct the cryostat
        cryo_lv = create_cryostat(cryostat_meta, from_gdml=True)
        pv = _place_pv(cryo_lv, "cryo_pv", world_lv, reg)
        reg.addVolumeRecursive(pv)

    if "lead_castle" in assemblies:
        # construct the bottom plate
        plate_meta = dim.get_bottom_plate_metadata()
        plate_lv = create_bottom_plate(plate_meta, from_gdml=True)

        z_pos = cryostat_meta.position_from_bottom + plate_meta.height / 2.0
        pv = _place_pv(plate_lv, "plate_pv", world_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        # construct the lead castle
        table = config.lead_castle_idx
        castle_dims = dim.get_castle_dimensions(table)
        castle_lv = create_lead_castle(table, castle_dims, from_gdml=True)

        z_pos = cryostat_meta.position_from_bottom - castle_dims.base.height / 2.0
        pv = _place_pv(castle_lv, "castle_pv", world_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

    if "source" in assemblies:
        if not construct_unverified:
            msg = (
                "Source assembly construction is implemented, but not verified. "
                "To proceed anyway, set construct_unverified to True."
            )
            raise NotImplementedError(msg)

        # basic information on the source
        source_type = config.source
        measurement = config.measurement

        # extract some metadata
        source_dims = dim.get_source_metadata(source_type)
        holder_dims = dim.get_source_holder_metadata(source_type, measurement)

        source_lv = create_source(source_type, source_dims, holder_dims, from_gdml=True)
        z_pos = hpge_meta.hades.source.z.position

        pv = _place_pv(source_lv, "source_pv", world_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        # construct th plate if needed
        if config.source == "th":
            th_plate_lv = create_th_plate(source_dims, from_gdml=True)
            pv = _place_pv(th_plate_lv, "th_plate_pv", world_lv, reg)
            reg.addVolumeRecursive(pv)

        s_holder_lv = create_source_holder(source_type, holder_dims, measurement, from_gdml=True)

        # TODO: this will break so we need to change it
        z_pos = -(hpge_meta.hades.source.z.position + holder_dims.source.top_plate_height / 2)

        pv = _place_pv(s_holder_lv, "source_holder_pv", world_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

    return reg
