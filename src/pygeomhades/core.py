from __future__ import annotations

import contextlib
import logging
from math import pi
import dbetto
from git import GitCommandError
from legendmeta import LegendMetadata
from pyg4ometry import geant4
from pyg4ometry import gdml
from pygeomtools.viewer import visualize
from pygeomtools.write import write_pygeom
from pygeomtools.detectors import generate_detector_macro

log = logging.getLogger(__name__)


def construct(
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

    #define all dimensions

    #Cryostat dimensions
    cryostat_height = 171.0
    cryostat_width = 101.6
    cryostat_thickness = 1.5
    position_cryostat_cavity_fromTop = 1.5
    position_cryostat_cavity_fromBottom = 0.8
    position_cryostat_fromBottom = 250.0

    # Base dimensions
    base_width_1 = 480.0
    base_depth_1 = 450.0
    base_height_1 = 500.0

    # Inner cavity dimensions
    inner_cavity_width_1 = 300.0
    inner_cavity_depth_1 = 250.0
    inner_cavity_height_1 = 500.0

    # Cavity dimensions
    cavity_width_1 = 120.0
    cavity_depth_1 = 100.0
    cavity_height_1 = 400.0

    # Top dimensions
    top_width_1 = 300.0
    top_depth_1 = 300.0
    top_height_1 = 90.0

    # Front dimensions
    front_width_1 = 160.0
    front_depth_1 = 100.0
    front_height_1 = 400.0

    # Bottom plate
    bottom_plate_width = 750.0
    bottom_plate_depth = 750.0
    bottom_plate_height = 15.0

    # Cavity bottom plate
    cavity_bottom_plate_width = 120.0
    cavity_bottom_plate_depth = 940.0
    cavity_bottom_plate_height = 20.0

    # Source holder dimensions
    source_holder_top_plate_height = 3.0
    source_holder_top_height = 10.0

    source_holder_top_plate_width = 30.0
    source_holder_top_inner_width = 20.0
    source_holder_inner_width = 87.0
    source_holder_bottom_inner_width = 102.0
    source_holder_outer_width = 108.0

    source_holder_topbottom_height = 6.1

    # Positions relative to cryostat
    position_detector_fromcryostat_z = 6.5
    position_holder_fromcryostat_z = 5.5
    position_wrap_fromcryostat_z = 5.5

    position_source_fromcryostat_phi = 0.0
    position_source_fromcryostat_r = 0.0
    position_source_fromcryostat_x = 0.0
    position_source_fromcryostat_y = -0.0
    position_source_fromcryostat_z = 200.0

    # Source dimensions
    source_height = 0.1
    source_width = 5.0

    # Source foil
    source_foil_height = 0.5
    source_foil_width = 26.0

    # Aluminum ring around source
    source_Alring_height = 3.0
    source_Alring_width_max = 30.0
    source_Alring_width_min = 26.0


    reg = geant4.Registry()

    # Create the world volume
    world_material = geant4.MaterialPredefined("G4_AIR")
    world = geant4.solid.Box("world", 10, 10, 10, reg, "m")
    world_lv = geant4.LogicalVolume(world, world_material, "world_lv", reg)
    reg.setWorld(world_lv)

    #create vacuum cavity
    vacuum_cavity_radius=(cryostat_width-2*cryostat_thickness)/2
    vacuum_cavity_z = (cryostat_height-position_cryostat_cavity_fromTop-position_cryostat_cavity_fromBottom)
    cavity_material = geant4.MaterialPredefined("G4_AIR")
    vacuum_cavity = geant4.solid.GenericPolycone("vacuum_cavity", 0.0, 2.0 * pi,  pR=([0.0, vacuum_cavity_radius, vacuum_cavity_z, 0.0]),  pZ=[0.0, 0.0, vacuum_cavity_z, vacuum_cavity_z],   lunit='mm', aunit='rad', registry=reg)
    cavity_lv = geant4.LogicalVolume(vacuum_cavity, cavity_material, "cavity_lv", reg)
    geant4.PhysicalVolume([0, 0, 0], [0, 0, position_cryostat_cavity_fromTop, "mm"], cavity_lv, "cavity_pv", world_lv, registry=reg)


    workingDir="/global/cfs/cdirs/m2676/users/biancacci/hades-sim/legend-pygeom-hades/geom_gdml/"


    #add detector
    reader_detector = gdml.Reader(f"{workingDir}detector.gdml")
    reg_detector  = reader_detector.getRegistry()
    detector_lv = reg_detector.getWorldVolume()
    detector_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, (position_detector_fromcryostat_z-position_cryostat_cavity_fromTop), "mm"], detector_lv, "hpge_physical", cavity_lv, registry=reg_detector)
    reg.addVolumeRecursive(detector_pv)

    #add wrap
    reader_wrap = gdml.Reader(f"{workingDir}wrap.gdml")
    reg_wrap  = reader_wrap.getRegistry()
    wrap_lv = reg_wrap.getWorldVolume()
    wrap_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, position_wrap_fromcryostat_z-position_cryostat_cavity_fromTop, "mm"], wrap_lv, "hpge_physical", cavity_lv, registry=reg_wrap)
    reg.addVolumeRecursive(wrap_pv)

    #add holder
    reader_holder = gdml.Reader(f"{workingDir}holder.gdml")
    reg_holder  = reader_holder.getRegistry()
    holder_lv = reg_holder.getWorldVolume()
    holder_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, position_holder_fromcryostat_z-position_cryostat_cavity_fromTop, "mm"], holder_lv, "hpge_physical", cavity_lv, registry=reg_holder)
    reg.addVolumeRecursive(holder_pv)


    #add bottom plate
    reader_plate = gdml.Reader(f"{workingDir}bottom_plate.gdml")
    reg_plate  = reader_plate.getRegistry()
    plate_lv = reg_plate.getWorldVolume()
    plate_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, position_cryostat_fromBottom+(bottom_plate_height)/2, "mm"], plate_lv, "hpge_physical", world_lv, registry=reg_plate)
    reg.addVolumeRecursive(plate_pv)

    #add lead castle
    reader_castle = gdml.Reader(f"{workingDir}lead_castle_table1.gdml")
    reg_castle  = reader_castle.getRegistry()
    castle_lv = reg_castle.getWorldVolume()
    castle_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, position_cryostat_fromBottom-(base_height_1)/2, "mm"], castle_lv, "hpge_physical", world_lv, registry=reg_castle)
    reg.addVolumeRecursive(castle_pv)

    #add source
    reader_source = gdml.Reader(f"{workingDir}source_encapsulated_ba_HS4.gdml")
    reg_source  = reader_source.getRegistry()
    source_lv = reg_source.getWorldVolume()
    source_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0,-position_source_fromcryostat_z, "mm"], source_lv, "hpge_physical", world_lv, registry=reg_source)
    reg.addVolumeRecursive(source_pv)

    #add source holder
    reader_sholder = gdml.Reader(f"{workingDir}plexiglass_source_holder.gdml")
    reg_sholder  = reader_sholder.getRegistry()
    sholder_lv = reg_sholder.getWorldVolume()
    sholder_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, -(position_source_fromcryostat_z+source_holder_top_plate_height/2), "mm"], sholder_lv, "hpge_physical", world_lv, registry=reg_sholder)
    reg.addVolumeRecursive(sholder_pv)

    #add cryostat
    reader_cryo = gdml.Reader(f"{workingDir}cryostat.gdml")
    reg_cryo  = reader_cryo.getRegistry()
    cryo_lv = reg_cryo.getWorldVolume()
    cryo_pv=geant4.PhysicalVolume([0, 0, 0], [0, 0, 0, "mm"], cryo_lv, "hpge_physical", world_lv, registry=reg_cryo)
    reg.addVolumeRecursive(cryo_pv)


    
    
    visualize(reg)
    
    #generate_detector_macro(reg, "pv_reg.mac")
    # write_pygeom(reg, "simple_teststand.gdml")
    return reg
