from __future__ import annotations

import fixed_dimensions as dim
import numpy as np
from pyg4ometry import gdml, geant4

# TODO: These functions seem very repetitive, maybe there is a way to reduce
#      but maybe when/if we move away from loading gdml files this will not be true


def place_vacuum_cavity(reg: geant4.Registry, world_lv: geant4.LogicalVolume) -> geant4.LogicalVolume:
    vacuum_cavity_radius = (dim.CRYOSTAT_WIDTH - 2 * dim.CRYOSTAT_THICKNESS) / 2
    vacuum_cavity_z = (
        dim.CRYOSTAT_HEIGHT - dim.POSITION_CRYOSTAT_CAVITY_FROM_TOP - dim.POSITION_CRYOSTAT_CAVITY_FROM_BOTTOM
    )
    cavity_material = geant4.MaterialPredefined("G4_AIR")
    vacuum_cavity = geant4.solid.GenericPolycone(
        "vacuum_cavity",
        0.0,
        2.0 * np.pi,
        pR=([0.0, vacuum_cavity_radius, vacuum_cavity_z, 0.0]),
        pZ=[0.0, 0.0, vacuum_cavity_z, vacuum_cavity_z],
        lunit="mm",
        aunit="rad",
        registry=reg,
    )
    cavity_lv = geant4.LogicalVolume(vacuum_cavity, cavity_material, "cavity_lv", reg)
    geant4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, dim.POSITION_CRYOSTAT_CAVITY_FROM_TOP, "mm"],
        cavity_lv,
        "cavity_pv",
        world_lv,
        registry=reg,
    )

    return cavity_lv


def place_detector(
    reg: geant4.Registry, cavity_lv: geant4.LogicalVolume, gdml_dir: str | None = None
) -> None:
    if gdml_dir:
        # add detector
        reader_detector = gdml.Reader(f"{gdml_dir}detector.gdml")
        reg_detector = reader_detector.getRegistry()
        detector_lv = reg_detector.getWorldVolume()
        detector_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, (dim.POSITION_DETECTOR_FROM_CRYOSTAT_Z - dim.POSITION_CRYOSTAT_CAVITY_FROM_TOP), "mm"],
            detector_lv,
            "hpge_physical",
            cavity_lv,
            registry=reg_detector,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)

    reg.addVolumeRecursive(detector_pv)


def place_wrap(reg: geant4.Registry, cavity_lv: geant4.LogicalVolume, gdml_dir: str | None = None) -> None:
    # add wrap
    if gdml_dir:
        reader_wrap = gdml.Reader(f"{gdml_dir}wrap.gdml")
        reg_wrap = reader_wrap.getRegistry()
        wrap_lv = reg_wrap.getWorldVolume()
        wrap_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.POSITION_WRAP_FROM_CRYOSTAT_Z - dim.POSITION_CRYOSTAT_CAVITY_FROM_TOP, "mm"],
            wrap_lv,
            "hpge_physical",
            cavity_lv,
            registry=reg_wrap,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(wrap_pv)


def place_holder(reg: geant4.Registry, cavity_lv: geant4.LogicalVolume, gdml_dir: str | None = None) -> None:
    if gdml_dir:
        # add holder
        reader_holder = gdml.Reader(f"{gdml_dir}holder.gdml")
        reg_holder = reader_holder.getRegistry()
        holder_lv = reg_holder.getWorldVolume()
        holder_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.POSITION_HOLDER_FROM_CRYOSTAT_Z - dim.POSITION_CRYOSTAT_CAVITY_FROM_TOP, "mm"],
            holder_lv,
            "hpge_physical",
            cavity_lv,
            registry=reg_holder,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(holder_pv)


def place_bottom_plate(
    reg: geant4.Registry, world_lv: geant4.LogicalVolume, gdml_dir: str | None = None
) -> None:
    if gdml_dir:
        # add bottom plate
        reader_plate = gdml.Reader(f"{gdml_dir}bottom_plate.gdml")
        reg_plate = reader_plate.getRegistry()
        plate_lv = reg_plate.getWorldVolume()
        plate_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.POSITION_CRYOSTAT_CAVITY_FROM_BOTTOM + (dim.BOTTOM_PLATE_HEIGHT) / 2, "mm"],
            plate_lv,
            "hpge_physical",
            world_lv,
            registry=reg_plate,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(plate_pv)


def place_lead_castle(
    reg: geant4.Registry, world_lv: geant4.LogicalVolume, gdml_dir: str | None = None
) -> None:
    if gdml_dir:
        # add lead castle
        reader_castle = gdml.Reader(f"{gdml_dir}lead_castle_table1.gdml")
        reg_castle = reader_castle.getRegistry()
        castle_lv = reg_castle.getWorldVolume()
        castle_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, dim.POSITION_CRYOSTAT_CAVITY_FROM_BOTTOM - (dim.BASE_HEIGHT) / 2, "mm"],
            castle_lv,
            "hpge_physical",
            world_lv,
            registry=reg_castle,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(castle_pv)


def place_source(reg: geant4.Registry, world_lv: geant4.LogicalVolume, gdml_dir: str | None = None) -> None:
    if gdml_dir:
        # TODO: replace this with a generic reader?
        reader_source = gdml.Reader(f"{gdml_dir}source_encapsulated_ba_HS4.gdml")
        reg_source = reader_source.getRegistry()
        source_lv = reg_source.getWorldVolume()
        source_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, -dim.POSITION_SOURCE_FROM_CRYOSTAT_Z, "mm"],
            source_lv,
            "hpge_physical",
            world_lv,
            registry=reg_source,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(source_pv)


def place_source_holder(
    reg: geant4.Registry, world_lv: geant4.LogicalVolume, gdml_dir: str | None = None
) -> None:
    if gdml_dir:
        reader_s_holder = gdml.Reader(f"{gdml_dir}plexiglass_source_holder.gdml")
        reg_s_holder = reader_s_holder.getRegistry()
        s_holder_lv = reg_s_holder.getWorldVolume()
        s_holder_pv = geant4.PhysicalVolume(
            [0, 0, 0],
            [0, 0, -(dim.POSITION_SOURCE_FROM_CRYOSTAT_Z + dim.SOURCE_HOLDER_TOP_PLATE_HEIGHT / 2), "mm"],
            s_holder_lv,
            "hpge_physical",
            world_lv,
            registry=reg_s_holder,
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(s_holder_pv)


def place_cryostat(reg: geant4.Registry, world_lv: geant4.LogicalVolume, gdml_dir: str | None = None) -> None:
    if gdml_dir:
        reader_cryo = gdml.Reader(f"{gdml_dir}cryostat.gdml")
        reg_cryo = reader_cryo.getRegistry()
        cryo_lv = reg_cryo.getWorldVolume()
        cryo_pv = geant4.PhysicalVolume(
            [0, 0, 0], [0, 0, 0, "mm"], cryo_lv, "hpge_physical", world_lv, registry=reg_cryo
        )
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    reg.addVolumeRecursive(cryo_pv)
