from __future__ import annotations

from pathlib import Path

import numpy as np
from dbetto import AttrsDict
from pyg4ometry import geant4
from pygeomhpges import make_hpge

from pygeomhades import dimensions as dim
from pygeomhades.utils import amend_gdml


def create_vacuum_cavity(cryostat_metadata: AttrsDict, registry: geant4.Registry) -> geant4.LogicalVolume:
    """Construct the vacuum cavity.

    Parameters
    ----------
    cryostat
        The dimensions of the various parts of the cryostat, should have
        the following format

        .. code-block:: yaml

            cryostat:
                width: 200
                thickness: 2
                height: 200
                position_cavity_from_top: 10
                position_cavity_from_bottom: 20,
                position_from_bottom: 100

    registry
        The registry to add the geometry to.

    Returns
    -------
    The logical volume for the cavity.
    """
    vacuum_cavity_radius = (cryostat_metadata["width"] - 2 * cryostat_metadata["thickness"]) / 2
    vacuum_cavity_z = (
        cryostat_metadata["height"]
        - cryostat_metadata["position_cavity_from_top"]
        - cryostat_metadata["position_cavity_from_bottom"]
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
        registry=registry,
    )
    return geant4.LogicalVolume(vacuum_cavity, cavity_material, "cavity_lv", registry)


def create_detector(reg: geant4.Registry, ged_meta_dict: AttrsDict) -> geant4.LogicalVolume:
    """Construct the detector logical volume"""

    return make_hpge(ged_meta_dict, name=ged_meta_dict.name, registry=reg)


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
        plate = dim.bottom_plate
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
            lead_castle = dim.lead_castle_1
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
            lead_castle = dim.lead_castle_2
            replacements = {
                "base_width_2": lead_castle["base_width"],
                "base_depth_2": lead_castle["base_depth"],
                "base_height_2": lead_castle["base_height"],
                "inner_cavity_width_2": lead_castle["inner_cavity_width"],
                "inner_cavity_depth_2": lead_castle["inner_cavity_depth"],
                "inner_cavity_height_2": lead_castle["inner_cavity_height"],
                "top_width_2": lead_castle["top_width"],
                "top_depth_2": lead_castle["top_depth"],
                "top_height_2": lead_castle["top_height"],
                "copper_plate_width": lead_castle["copper_plate_width"],
                "copper_plate_depth": lead_castle["copper_plate_depth"],
                "copper_plate_height": lead_castle["copper_plate_height"],
            }
        else:
            msg = "there are only 2 lead castles currently in the gdml"
            raise RuntimeError(msg)
        castle_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return castle_lv


def create_source(config: dict, from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        source = dim.source
        source_holder = dim.source_holder
        if config["source"] == "am_collimated":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/source_am_collimated_dummy.gdml"
            replacements = {
                "source_height": source["height"],
                "source_width": source["width"],
                "source_capsule_height": source["capsule"]["height"],
                "source_capsule_width": source["capsule"]["width"],
                "window_source": source["collimator"]["window"],
                "collimator_height": source["collimator"]["height"],
                "collimator_depth": source["collimator"]["depth"],
                "collimator_width": source["collimator"]["width"],
                "collimator_beam_height": source["collimator"]["beam_height"],
                "collimator_beam_width": source["collimator"]["beam_width"],
            }
        elif config["source"] == "am":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/source_am_dummy.gdml"
            replacements = {
                "source_height": source["height"],
                "source_width": source["width"],
                "source_capsule_height": source["capsule"]["height"],
                "source_capsule_width": source["capsule"]["width"],
                "source_capsule_depth": source["capsule"]["depth"],
            }
        elif config["source"] in ["ba", "co"]:
            dummy_gdml_path = Path(__file__).parent / f"models/dummy/source_{config['source']}_dummy.gdml"
            replacements = {
                "source_height": source["height"],
                "source_width": source["width"],
                "source_foil_height": source["foil"]["height"],
                "source_Alring_height": source["al_ring"]["height"],
                "source_Alring_width_min": source["al_ring"]["width_min"],
                "source_Alring_width_max": source["al_ring"]["width_max"],
            }
        elif config["source"] == "th":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/source_th_dummy.gdml"
            replacements = {
                "source_height": source["height"],
                "source_width": source["width"],
                "source_capsule_height": source["capsule"]["height"],
                "source_capsule_width": source["capsule"]["width"],
                "source_epoxy_height": source["epoxy"]["height"],
                "source_epoxy_width": source["epoxy"]["width"],
                "CuSource_holder_height": source_holder["copper"]["height"],
                "CuSource_holder_width": source_holder["copper"]["width"],
                "CuSource_holder_cavity_width": source_holder["copper"]["cavity_width"],
                "CuSource_holder_bottom_height": source_holder["copper"]["bottom_height"],
                "CuSource_holder_bottom_width": source_holder["copper"]["bottom_width"],
                "source_offset_height": source["offset_height"],
            }
        else:
            msg = "only 5 sources have been defined"
            raise RuntimeError(msg)
        source_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return source_lv


def create_th_plate(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        dummy_gdml_path = Path(__file__).parent / "models/dummy/source_th_plates_dummy.gdml"
        source = dim.source
        replacements = {
            "source_plates_height": source["plates"]["height"],
            "source_plates_width": source["plates"]["width"],
            "source_plates_cavity_width": source["plates"]["cavity_width"],
        }
        th_plate_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return th_plate_lv


def create_source_holder(config: dict, from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        source_holder = dim.source_holder
        if config["source"] == "th" and config["measurement_type"] == "lat":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/source_holder_th_lat_dummy.gdml"
            replacements = {
                "cavity_source_holder_height": source_holder["lat"]["cavity_height"],
                "source_holder_height": source_holder["lat"]["height"],
                "source_holder_outer_width": source_holder["outer_width"],
                "source_holder_inner_width": source_holder["inner_width"],
                "cavity_source_holder_width": source_holder["holder_width"],
            }
        elif config["source"] in ["am_collimated", "ba", "co", "th"]:
            dummy_gdml_path = Path(__file__).parent / "models/dummy/source_holder_dummy.gdml"
            replacements = {
                "source_holder_top_plate_height": source_holder["top"]["top_plate_height"],
                "source_holder_top_height": source_holder["top"]["top_height"],
                "source_holder_topbottom_height": source_holder["top"]["top_bottom_height"],
                "source_holder_top_plate_width": source_holder["top"]["top_plate_width"],
                "source_holder_top_inner_width": source_holder["top"]["top_inner_width"],
                "source_holder_inner_width": source_holder["inner_width"],
                "source_holder_bottom_inner_width": source_holder["top"]["bottom_inner_width"],
                "source_holder_outer_width": source_holder["outer_width"],
                "position_source_fromcryostat_z": dim.positions_from_cryostat["source"]["z"],
            }
        elif config["source"] == "am":
            dummy_gdml_path = Path(__file__).parent / "models/dummy/source_holder_am_dummy.gdml"
            replacements = {
                "source_holder_top_height": source_holder["am"]["top_height"],
                "position_source_fromcryostat_z": dim.positions_from_cryostat["source"]["z"],
                "source_holder_top_plate_height": source_holder["am"]["top_plate_height"],
                "source_holder_top_plate_width": source_holder["am"]["top_plate_width"],
                "source_holder_top_plate_depth": source_holder["am"]["top_plate_depth"],
                "source_holder_topbottom_height": source_holder["am"]["top_bottom_height"],
                "source_holder_top_inner_width": source_holder["am"]["top_inner_width"],
                "source_holder_top_inner_depth": source_holder["am"]["top_inner_depth"],
                "source_holder_inner_width": source_holder["inner_width"],
                "source_holder_bottom_inner_width": source_holder["am"]["bottom_inner_width"],
                "source_holder_outer_width": source_holder["outer_width"],
            }
        else:
            msg = "source not in available sources"
            raise RuntimeError(msg)
        s_holder_lv = amend_gdml(dummy_gdml_path, replacements).getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return s_holder_lv


def create_cryostat(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        dummy_gdml_path = Path(__file__).parent / "models/dummy/cryostat_dummy.gdml"
        cryostat = dim.cryostat
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
