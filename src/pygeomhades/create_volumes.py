from __future__ import annotations

from importlib import resources

import numpy as np
from dbetto import AttrsDict
from pyg4ometry import geant4

from pygeomhades import dimensions as dim
from pygeomhades.utils import read_gdml_with_replacements


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


def create_wrap(wrap_metadata: AttrsDict, from_gdml: bool = False) -> geant4.LogicalVolume:
    """Create the mylar wrap.

    :: warning

        The returned logical volume belongs to its own registry,
        it is necessary to call {func}`reg.addVolumeRecursive` on
        the produced PhysicalVolume to get a sane registry.

    Parameters
    ----------
    wrap_metadata
        The information on the dimensions of the mylar wrap,
        should be of the format:

        .. code-block:: yaml

            outer:
                height_in_mm: 100
                radius_in_mm: 100
            inner:
                height_in_mm: 99
                radius_in_mm: 99

    from_gdml
        whether to read the geometry from GDML or construct it directly.
    """
    if from_gdml:
        dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "wrap_dummy.gdml"

        replacements = {
            "wrap_outer_height_in_mm": wrap_metadata.outer.height_in_mm,
            "wrap_outer_radius_in_mm": wrap_metadata.outer.radius_in_mm,
            "wrap_inner_radius_in_mm": wrap_metadata.inner.radius_in_mm,
            "wrap_top_thickness_in_mm": wrap_metadata.outer.height_in_mm - wrap_metadata.inner.height_in_mm,
        }
        wrap_lv = read_gdml_with_replacements(dummy_gdml_path, replacements)
    else:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    return wrap_lv


def create_holder(holder_meta: AttrsDict, det_type: str, from_gdml: bool = True) -> geant4.LogicalVolume:
    """Construct the holder geometry

    Parameters
    ----------
    holder_meta
        The metadata describing the holder geometry, should be of the format:

        .. code-block:: yaml

            cylinder:
                inner:
                    height_in_mm: 100
                    radius_in_mm: 100
                outer:
                    height_in_mm: 104
                    radius_in_mm: 104
            bottom_cyl:
                inner:
                    height_in_mm: 100
                    radius_in_mm: 100
                outer:
                    height_in_mm: 104
                    radius_in_mm: 104
            rings:
                position_top_ring_in_mm: 20
                position_bottom_ring_in_mm: 30
                radius_in_mm: 150
                height_in_mm: 10
            edge:
                height_in_mm: 1000

    det_type
        Detector type.
    from_gdml
        Whether to construct from a GDML file

    """

    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    if det_type == "icpc":
        dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "holder_icpc_dummy.gdml"

        rings = holder_meta["rings"]
        cylinder = holder_meta["cylinder"]
        bottom_cylinder = holder_meta["bottom_cyl"]

        replacements = {
            "max_radius_in_mm": rings.radius_in_mm,
            "outer_height_in_mm": cylinder.outer.height_in_mm,
            "inner_height_in_mm": cylinder.inner.height_in_mm,
            "outer_radius_in_mm": cylinder.outer.radius_in_mm,
            "inner_radius_in_mm": cylinder.inner.radius_in_mm,
            "outer_bottom_cyl_radius_in_mm": bottom_cylinder.outer.radius_in_mm,
            "inner_bottom_cyl_radius_in_mm": bottom_cylinder.inner.radius_in_mm,
            "edge_height_in_mm": holder_meta.edge.height_in_mm,
            "pos_top_ring_in_mm": rings.position_top_ring_in_mm,
            "pos_bottom_ring_in_mm": rings.position_bottom_ring_in_mm,
            "end_top_ring_in_mm": rings.position_top_ring_in_mm + rings.height_in_mm,
            "end_bottom_ring_in_mm": rings.position_bottom_ring_in_mm + rings.height_in_mm,
            "end_bottom_cyl_outer_in_mm": cylinder.outer.height_in_mm + bottom_cylinder.outer.height_in_mm,
            "end_bottom_cyl_inner_in_mm": cylinder.inner.height_in_mm + bottom_cylinder.inner.height_in_mm,
        }

    elif det_type == "bege":
        dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "holder_bege_dummy.gdml"

        rings = holder_meta["rings"]
        cylinder = holder_meta["cylinder"]
        bottom_cylinder = holder_meta["bottom_cyl"]

        replacements = {
            "max_radius_in_mm": rings.radius_in_mm,
            "outer_height_in_mm": cylinder.outer.height_in_mm,
            "inner_height_in_mm": cylinder.inner.height_in_mm,
            "outer_radius_in_mm": cylinder.outer.radius_in_mm,
            "inner_radius_in_mm": cylinder.inner.radius_in_mm,
            "position_top_ring_in_mm": rings.position_top_ring_in_mm,
            "end_top_ring_in_mm": rings.height_in_mm + rings.position_top_ring_in_mm,
        }
    else:
        msg = "cannot construct geometry for coax or ppc"
        raise NotImplementedError(msg)

    return read_gdml_with_replacements(dummy_gdml_path, replacements)


def create_bottom_plate(plate_metadata: AttrsDict, from_gdml: bool = True) -> geant4.Registry:
    """Create the bottom plate.

    Parameters
    ----------
    plate_metadata
        Metadata describing the position of the bottom plate.
        This should have the format:

        .. code-block:: yaml

            width: 100
            depth: 200
            height: 300
            cavity:
                width: 100
                depth: 200
                height: 200
    from_gdml
        Whether to construct from a GDML file

    """
    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "bottom_plate_dummy.gdml"

    replacements = {
        "bottom_plate_width": plate_metadata.width,
        "bottom_plate_depth": plate_metadata.depth,
        "bottom_plate_height": plate_metadata.height,
        "bottom_cavity_plate_width": plate_metadata.cavity.width,
        "bottom_cavity_plate_depth": plate_metadata.cavity.depth,
        "bottom_cavity_plate_height": plate_metadata.cavity.height,
    }
    return read_gdml_with_replacements(dummy_gdml_path, replacements)


def create_lead_castle(
    table_num: int, castle_dimensions: AttrsDict, from_gdml: bool = True
) -> geant4.LogicalVolume:
    """Create the lead castle.

    Parameters
    ----------
    table_number
        Which table the measurements were taken on (1 or 2).
    castle_dimensions
        The metadata describing the lead castle dimensions. This should
        have the fields "base", "inner_cavity", "cavity",
        "top", "front" and "copper_plate".

        Each should have a subdictionary with this format:

        .. code-block:: yaml

            base:
                height: 100
                depth: 100
                width: 100

    from_gdml
        Whether to construct from a GDML file
    """

    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    if table_num not in [1, 2]:
        msg = f"Table number must be 1 or 2 not {table_num}"
        raise ValueError(msg)

    dummy_gdml_path = (
        resources.files("pygeomhades") / "models" / "dummy" / f"lead_castle_table{table_num}_dummy.gdml"
    )

    if table_num == 1:
        replacements = {
            "base_width_1": castle_dimensions.base.width,
            "base_depth_1": castle_dimensions.base.depth,
            "base_height_1": castle_dimensions.base.height,
            "inner_cavity_width_1": castle_dimensions.inner_cavity.width,
            "inner_cavity_depth_1": castle_dimensions.inner_cavity.depth,
            "inner_cavity_height_1": castle_dimensions.inner_cavity.height,
            "cavity_width_1": castle_dimensions.cavity.width,
            "cavity_depth_1": castle_dimensions.cavity.depth,
            "cavity_height_1": castle_dimensions.cavity.height,
            "top_width_1": castle_dimensions.top.width,
            "top_depth_1": castle_dimensions.top.depth,
            "top_height_1": castle_dimensions.top.height,
            "front_width_1": castle_dimensions.front.width,
            "front_depth_1": castle_dimensions.front.depth,
            "front_height_1": castle_dimensions.front.height,
        }

    elif table_num == 2:
        replacements = {
            "base_width_2": castle_dimensions.base.width,
            "base_depth_2": castle_dimensions.base.depth,
            "base_height_2": castle_dimensions.base.height,
            "inner_cavity_width_2": castle_dimensions.inner_cavity.width,
            "inner_cavity_depth_2": castle_dimensions.inner_cavity.depth,
            "inner_cavity_height_2": castle_dimensions.inner_cavity.height,
            "top_width_2": castle_dimensions.top.width,
            "top_depth_2": castle_dimensions.top.depth,
            "top_height_2": castle_dimensions.top.height,
            "copper_plate_width": castle_dimensions.copper_plate.width,
            "copper_plate_depth": castle_dimensions.copper_plate.depth,
            "copper_plate_height": castle_dimensions.copper_plate.height,
        }

    return read_gdml_with_replacements(dummy_gdml_path, replacements, vol_name="Lead_castle")


def create_source(
    source_type: str, source_dims: AttrsDict, holder_dims: AttrsDict | None, from_gdml: bool = False
) -> geant4.LogicalVolume:
    """Create the geometry of the source.

    Parameters
    ----------
    source_type
        The type of source (am_collimated, am, ba, co or th)
    source_dims
        Metadata describing the source geometry.
        Should be of the following format:

        .. code-block:: yaml

            height: 0.0
            width: 0.0

            foil:
                height: 0.0
                width: 0.0

            al_ring:
                height: 0.0
                width_max: 0.0
                width_min: 0.0

            capsule:
                width: 0.0
                depth: 0.0
                height: 0.0

            collimator:
                width: 0.0
                depth: 0.0
                height: 0.0
                beam_width: 0.0
                beam_height: 0.0
                window: 0.0

            epoxy:
                height: 0.0
                width: 0.0

            plates:
                height: 0.0
                width: 0.0
                cavity_width: 0.0

            offset_height: 0.0

    holder_dims
        Dimensions of the source holder (see {func}`get_source_holder`).

    from_gdml
        Whether to construct from a GDML file
    """

    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / f"source_{source_type}_dummy.gdml"

    source = source_dims

    if source_type == "am_collimated":
        replacements = {
            "source_height": source.height,
            "source_width": source.width,
            "source_capsule_height": source.capsule.height,
            "source_capsule_width": source.capsule.width,
            "window_source": source.collimator.window,
            "collimator_height": source.collimator.height,
            "collimator_depth": source.collimator.depth,
            "collimator_width": source.collimator.width,
            "collimator_beam_height": source.collimator.beam_height,
            "collimator_beam_width": source.collimator.beam_width,
        }

    elif source_type == "am":
        replacements = {
            "source_height": source.height,
            "source_width": source.width,
            "source_capsule_height": source.capsule.height,
            "source_capsule_width": source.capsule.width,
            "source_capsule_depth": source.capsule.depth,
        }

    elif source_type in ["ba", "co"]:
        replacements = {
            "source_height": source.height,
            "source_width": source.width,
            "source_foil_height": source.foil.height,
            "source_Alring_height": source.al_ring.height,
            "source_Alring_width_min": source.al_ring.width_min,
            "source_Alring_width_max": source.al_ring.width_max,
        }

    elif source_type == "th":
        source_holder = holder_dims

        replacements = {
            "source_height": source.height,
            "source_width": source.width,
            "source_capsule_height": source.capsule.height,
            "source_capsule_width": source.capsule.width,
            "source_epoxy_height": source.epoxy.height,
            "source_epoxy_width": source.epoxy.width,
            "CuSource_holder_height": source_holder.copper.height,
            "CuSource_holder_width": source_holder.copper.width,
            "CuSource_holder_cavity_width": source_holder.copper.cavity_width,
            "CuSource_holder_bottom_height": source_holder.copper.bottom_height,
            "CuSource_holder_bottom_width": source_holder.copper.bottom_width,
            "source_offset_height": source.offset_height,
        }

    else:
        msg = f"source type of {source_type} is not defined."
        raise RuntimeError(msg)

    return read_gdml_with_replacements(dummy_gdml_path, replacements)


def create_th_plate(source_dims: AttrsDict, from_gdml: bool = False) -> geant4.LogicalVolume:
    """Construct the plate for the Th source

    Parameters
    ----------
    source_dims
        See {func}`create_source` for more information.
    from_gdml
        Whether to construct from a GDML file

    """
    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "source_th_plates_dummy.gdml"
    source = source_dims

    replacements = {
        "source_plates_height": source.plates.height,
        "source_plates_width": source.plates.width,
        "source_plates_cavity_width": source.plates.cavity_width,
    }

    return read_gdml_with_replacements(dummy_gdml_path, replacements)


def create_source_holder(
    source_type: str, holder_dims: AttrsDict, meas_type: str = "lat", from_gdml: bool = True
) -> geant4.LogicalVolume:
    """Get the source holder geometry.

    Parameters
    ----------
    source_type
        The type of source (am_collimated, am, ba, co or th)
    holder_dims
        The dimensions of the source holder, should be of the format:

        .. code-block:: yaml
            source:
                top_plate_height: 10.0
                top_plate_width: 10.0
                top_height: 2.0
                top_inner_width: 2.0
                top_bottom_height: 2.0
                bottom_inner_width: 2.0
            outer_width: 100.0
            inner_width: 10.0

    meas_type
        The measurement type (for th only) either lat or top.
    from_gdml
        Whether to construct from a GDML file
    """

    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    source_holder = holder_dims
    dummy_path = resources.files("pygeomhades") / "models" / "dummy"

    if source_type == "th" and meas_type == "lat":
        dummy_gdml_path = dummy_path / "source_holder_th_lat_dummy.gdml"

        replacements = {
            "cavity_source_holder_height": source_holder.source.cavity_height,
            "source_holder_height": source_holder.source.height,
            "source_holder_outer_width": source_holder.outer_width,
            "source_holder_inner_width": source_holder.inner_width,
            "cavity_source_holder_width": source_holder.holder_width,
        }

    elif source_type in ["am_collimated", "ba", "co", "th"]:
        dummy_gdml_path = dummy_path / "source_holder_dummy.gdml"

        replacements = {
            "source_holder_top_plate_height": source_holder.source.top_plate_height,
            "source_holder_top_height": source_holder.source.top_height,
            "source_holder_topbottom_height": source_holder.source.top_bottom_height,
            "source_holder_top_plate_width": source_holder.source.top_plate_width,
            "source_holder_top_inner_width": source_holder.source.top_inner_width,
            "source_holder_inner_width": source_holder.inner_width,
            "source_holder_bottom_inner_width": source_holder.source.bottom_inner_width,
            "source_holder_outer_width": source_holder.outer_width,
            "position_source_fromcryostat_z": dim.positions_from_cryostat.source.z,
        }

    elif source_type == "am":
        dummy_gdml_path = dummy_path / "source_holder_am_dummy.gdml"

        replacements = {
            "source_holder_top_height": source_holder.source.top_height,
            "position_source_fromcryostat_z": dim.positions_from_cryostat.source.z,
            "source_holder_top_plate_height": source_holder.source.top_plate_height,
            "source_holder_top_plate_width": source_holder.source.top_plate_width,
            "source_holder_top_plate_depth": source_holder.source.top_plate_depth,
            "source_holder_topbottom_height": source_holder.source.top_bottom_height,
            "source_holder_top_inner_width": source_holder.source.top_inner_width,
            "source_holder_top_inner_depth": source_holder.source.top_inner_depth,
            "source_holder_inner_width": source_holder.inner_width,
            "source_holder_bottom_inner_width": source_holder.source.bottom_inner_width,
            "source_holder_outer_width": source_holder.outer_width,
        }

    else:
        msg = f"source type {source_type} not implemented."
        raise RuntimeError(msg)

    return read_gdml_with_replacements(dummy_gdml_path, replacements)


def create_cryostat(cryostat_meta: AttrsDict, from_gdml: bool = True) -> geant4.LogicalVolume:
    """Create the cryostat logical volume.

    Parameters
    ----------
    cryostat_meta
        Metadata describing the cryostat geometry (see {func}`create_wrap`) for details.
    from_gdml
        Whether to construct from a GDML file

    """

    if not from_gdml:
        msg = "cannot construct geometry without the gdml for now"
        raise NotImplementedError(msg)

    dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "cryostat_dummy.gdml"

    replacements = {
        "cryostat_height": cryostat_meta.height,
        "cryostat_width": cryostat_meta.width,
        "cryostat_thickness": cryostat_meta.thickness,
        "position_cryostat_cavity_fromTop": cryostat_meta.position_cavity_from_top,
        "position_cryostat_cavity_fromBottom": cryostat_meta.position_cavity_from_bottom,
    }
    return read_gdml_with_replacements(dummy_gdml_path, replacements)
