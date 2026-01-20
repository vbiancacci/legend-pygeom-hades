from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
from pyg4ometry import gdml, geant4
from pygeomhpges import make_hpge

from pygeomhades import fixed_dimensions as dim
from pygeomhades.utils import _read_gdml_model

# TODO: These functions seem very repetitive, maybe there is a way to reduce
#      but maybe when/if we move away from loading gdml files this will not be true


def write_gdml(reg: gdml.Registry, gdml_file_name: str | Path) -> None:
    w = gdml.Writer()
    w.addDetector(reg)
    w.write(gdml_file_name)


def amend_gdml(
    dummy_gdml_path: Path,
    replacements: dict,
    write_file: bool = False,
    gdml_file_name: str | Path = "test.gdml",
) -> geant4.Registry:
    gdml_text = dummy_gdml_path.read_text()

    for key, val in replacements.items():
        gdml_text = gdml_text.replace(key, f"{val:.{1}f}")

    with tempfile.NamedTemporaryFile("w+", suffix=".gdml") as f:
        f.write(gdml_text)
        f.flush()
        reader = gdml.Reader(f.name)

        if write_file:
            write_gdml(reader.getRegistry(), gdml_file_name)

        return reader.getRegistry()


def create_vacuum_cavity(reg: geant4.Registry) -> geant4.LogicalVolume:
    vacuum_cavity_radius = (dim.CRYOSTAT["width"] - 2 * dim.CRYOSTAT["thickness"]) / 2
    vacuum_cavity_z = (
        dim.CRYOSTAT["height"]
        - dim.CRYOSTAT["position_cavity_from_top"]
        - dim.CRYOSTAT["position_cavity_from_bottom"]
    )
    cavity_material = geant4.MaterialPredefined("G4_Galactic")
    vacuum_cavity = geant4.solid.GenericPolycone(
        "vacuum_cavity",
        0.0,
        2.0 * np.pi,
        pR=([0.0, vacuum_cavity_radius, vacuum_cavity_radius, 0.0]),
        pZ=[0.0, 0.0, vacuum_cavity_z, vacuum_cavity_z],
        lunit="mm",
        aunit="rad",
        registry=reg,
    )
    return geant4.LogicalVolume(vacuum_cavity, cavity_material, "cavity_lv", reg)


def create_detector(reg: geant4.Registry, ged_meta_dict) -> geant4.LogicalVolume:
    return make_hpge(ged_meta_dict, name="hpge_lv", registry=reg)


def create_wrap(detector_meta: dict, from_gdml: bool = False) -> geant4.LogicalVolume:
    wrap = detector_meta["hades"]["dimensions"]["wrap"]["geometry"]
    if from_gdml:
        dummy_gdml_path = Path(__file__).parent / "models/dummy/wrap_dummy.gdml"
        replacements = {
            "wrap_outer_height_in_mm": wrap["outer"]["height_in_mm"],
            "wrap_outer_radius_in_mm": wrap["outer"]["radius_in_mm"],
            "wrap_inner_radius_in_mm": wrap["inner"]["radius_in_mm"],
            "wrap_top_thickness_in_mm": wrap["outer"]["height_in_mm"] - wrap["inner"]["height_in_mm"],
        }
        wrap_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return wrap_lv


def create_holder(detector_meta: dict, from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        holder = detector_meta["hades"]["dimensions"]["holder"]["geometry"]
        if detector_meta["type"] == "icpc":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/holder_icpc_dummy.gdml"
            replacements = {
                "max_radius_in_mm": holder["rings"]["radius_in_mm"],
                "outer_height_in_mm": holder["cylinder"]["outer"]["height_in_mm"],
                "inner_height_in_mm": holder["cylinder"]["inner"]["height_in_mm"],
                "outer_radius_in_mm": holder["cylinder"]["outer"]["radius_in_mm"],
                "inner_radius_in_mm": holder["cylinder"]["inner"]["radius_in_mm"],
                "outer_bottom_cyl_radius_in_mm": holder["bottom_cyl"]["outer"]["radius_in_mm"],
                "inner_bottom_cyl_radius_in_mm": holder["bottom_cyl"]["inner"]["radius_in_mm"],
                "edge_height_in_mm": holder["edge"]["height_in_mm"],
                "pos_top_ring_in_mm": holder["rings"]["position_top_ring_in_mm"],
                "pos_bottom_ring_in_mm": holder["rings"]["position_bottom_ring_in_mm"],
                "end_top_ring_in_mm": holder["rings"]["position_top_ring_in_mm"]
                + holder["rings"]["height_in_mm"],
                "end_bottom_ring_in_mm": holder["rings"]["position_bottom_ring_in_mm"]
                + holder["rings"]["height_in_mm"],
                "end_bottom_cyl_outer_in_mm": holder["cylinder"]["outer"]["height_in_mm"]
                + holder["bottom_cyl"]["outer"]["height_in_mm"],
                "end_bottom_cyl_inner_in_mm": holder["cylinder"]["outer"]["height_in_mm"]
                + holder["bottom_cyl"]["inner"]["height_in_mm"],
            }
        elif detector_meta["type"] == "bege":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/holder_bege_dummy.gdml"
            replacements = {
                "max_radius_in_mm": holder["rings"]["radius_in_mm"],
                "outer_height_in_mm": holder["cylinder"]["outer"]["height_in_mm"],
                "inner_height_in_mm": holder["cylinder"]["inner"]["height_in_mm"],
                "outer_radius_in_mm": holder["cylinder"]["outer"]["radius_in_mm"],
                "inner_radius_in_mm": holder["cylinder"]["inner"]["radius_in_mm"],
                "position_top_ring_in_mm": holder["rings"]["position_top_ring_in_mm"],
                "end_top_ring_in_mm": holder["rings"]["height_in_mm"]
                + holder["rings"]["position_top_ring_in_mm"],
            }
        else:
            msg = "cannot construct geometry for coax or ppc"
            raise RuntimeError(msg)

        holder_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()

    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return holder_lv


def create_bottom_plate(from_gdml: bool = False) -> geant4.Registry:
    if from_gdml:
        dummy_gdml_path = Path(__file__).parent / "models/dummy/bottom_plate_dummy.gdml"
        plate = dim.BOTTOM_PLATE
        replacements = {
            "bottom_plate_width": plate["width"],
            "bottom_plate_depth": plate["depth"],
            "bottom_plate_height": plate["height"],
            "bottom_cavity_plate_width": plate["cavity_width"],
            "bottom_cavity_plate_depth": plate["cavity_depth"],
            "bottom_cavity_plate_height": plate["cavity_height"],
        }
        plate_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return plate_lv


def create_lead_castle(table_num: int, from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        if table_num == 1:
            dummy_gdml_path = Path(__file__).parent / "models/dummy/lead_castle_table1_dummy.gdml"
            lead_castle = dim.LEAD_CASTLE_1
            replacements = {
                "base_width_1": lead_castle["base_width"],
                "base_depth_1": lead_castle["base_depth"],
                "base_height_1": lead_castle["base_height"],
                "inner_cavity_width_1": lead_castle["inner_cavity_width"],
                "inner_cavity_depth_1": lead_castle["inner_cavity_depth"],
                "inner_cavity_height_1": lead_castle["inner_cavity_height"],
                "cavity_width_1": lead_castle["cavity_width"],
                "cavity_depth_1": lead_castle["cavity_depth"],
                "cavity_height_1": lead_castle["cavity_height"],
                "top_width_1": lead_castle["top_width"],
                "top_depth_1": lead_castle["top_depth"],
                "top_height_1": lead_castle["top_height"],
                "front_width_1": lead_castle["front_width"],
                "front_depth_1": lead_castle["front_depth"],
                "front_height_1": lead_castle["front_height"],
            }
        elif table_num == 2:
            dummy_gdml_path = Path(__file__).parent / "models/dummy/lead_castle_table2_dummy.gdml"
            lead_castle = dim.LEAD_CASTLE_2
            replacements = {}
        else:
            msg = "there are only 2 lead castles currently in the gdml"
            raise RuntimeError(msg)
        castle_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return castle_lv


def create_source(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        # TODO: replace this with a generic reader?
        reg_source = _read_gdml_model("source_encapsulated_ba_HS4.gdml")
        source_lv = reg_source.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return source_lv


def create_source_holder(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_s_holder = _read_gdml_model("plexiglass_source_holder.gdml")
        s_holder_lv = reg_s_holder.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return s_holder_lv


def create_cryostat(hpge_meta, from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        dummy_gdml_path = Path(__file__).parent / "models/dummy/cryostat_dummy.gdml"
        cryostat = dim.CRYOSTAT
        replacements = {
            "cryostat_height": cryostat["height"],
            "cryostat_width": cryostat["width"],
            "cryostat_thickness": cryostat["thickness"],
            "position_cryostat_cavity_fromTop": cryostat["position_cavity_from_top"],
            "position_cryostat_cavity_fromBottom": cryostat["position_cavity_from_bottom"],
        }
        cryo_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return cryo_lv
