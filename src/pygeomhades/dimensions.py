from __future__ import annotations

from dbetto import AttrsDict


def get_bottom_plate_metadata() -> AttrsDict:
    """Extract the metadata describing the bottom plate."""

    return AttrsDict(
        {
            "width": 750,
            "depth": 750,
            "height": 15,
            "cavity": {
                "width": 120,
                "depth": 940,  # <!--475*2-->
                "height": 20,
            },
        }
    )


def get_cryostat_metadata(det_type: str, order: int, xtal_slice: str) -> AttrsDict:
    """Extract the metadata corresponding the the cryostat

    In future this will be moved into external metadata.

    Parameters
    ----------
    det_type
        The detector type (should be icpc or bege).
    order
        The order number.
    xtal_slice
        The slice of the crystal (typically A or B).
    """
    cryostat = {
        "width": 101.6,
        "height": 122.2,
        "thickness": 1.5,
        "position_cavity_from_top": 1.5,
        "position_cavity_from_bottom": 0.8,
        "position_from_bottom": 250.0,
    }
    xl_orders = [3, 8, 9, 10]

    if det_type == "bege":
        cryostat["height"] = 122.2
        cryostat["width"] = 101.6

    elif (det_type == "icpc") and (order in xl_orders):
        cryostat["width"] = 114.3
    elif det_type == "icpc":
        cryostat["width"] = 101.6
    else:
        msg = "Only detector type icpc or bege are supported."
        raise ValueError(msg)

    # override batch 9
    if order == 9 and xtal_slice == "B":
        cryostat["width"] = 107.95

    return AttrsDict(cryostat)


source_holder = {
    "lat": {"height": 0.0, "cavity_height": 0.0, "cavity_width": 0.0},
    "am_HS6": {
        "top_height": 0.0,
        "top_inner_width": 0.0,
        "top_inner_depth": 0.0,
        "bottom_inner_width": 0.0,
        "top_bottom_height": 0.0,
        "top_plate_width": 0.0,
        "top_plate_depth": 0.0,
        "top_plate_height": 0.0,
    },
    "copper": {"height": 0.0, "width": 0.0, "cavity_width": 0.0, "bottom_height": 0.0, "bottom_width": 0.0},
    "top": {
        "top_plate_height": 0.0,
        "top_plate_width": 0.0,
        "top_height": 0.0,
        "top_inner_width": 0.0,
        "bottom_inner_width": 0.0,
        "top_bottom_height": 0.0,
    },
    "inner_width": 0.0,
    "holder_width": 0.0,
    "outer_width": 0.0,
}


def get_castle_dimensions(table_num: int) -> AttrsDict:
    """Extract the lead castle dimensions for a given table.

    Parameters
    ----------
    table_num
        The number of the table to use, can be 1 or 2.
    """

    if table_num == 1:
        lead_castle = {
            "base": {
                "width": 480,
                "depth": 450,
                "height": 500,
            },
            "inner_cavity": {
                "width": 300,
                "depth": 250,
                "height": 500,
            },
            "cavity": {
                "width": 120,
                "depth": 100,
                "height": 400,
            },
            "top": {
                "width": 300,
                "depth": 300,
                "height": 90,
            },
            "front": {
                "width": 160,
                "depth": 100,
                "height": 400,
            },
        }
    elif table_num == 2:
        lead_castle = {
            "base": {
                "width": 350,
                "depth": 350,
                "height": 400,
            },
            "inner_cavity": {
                "width": 250,
                "depth": 250,
                "height": 400,
            },
            "top": {
                "width": 200,
                "depth": 200,
                "height": 50,
            },
            "copper_plate": {
                "width": 350,
                "depth": 350,
                "height": 10,
            },
        }

    else:
        msg = "Table number must be 1 or 2"
        raise ValueError(msg)

    return AttrsDict(lead_castle)


def get_source_metadata(source_type: str, meas_type: str = "") -> AttrsDict:
    """Get the dimensions of the source and collimator.

    Parameters
    ----------
    source_type
        The type of source (am_HS1, am_HS6, ba_HS4, co_HS5 or th_HS2)
    meas_type
        The measurement (for th_HS2 only) either lat or top.
    """
    if source_type == "am_HS1":
        source = {
            "height": 2.0,
            "width": 1.0,
            "capsule": {
                "width": 20,
                "depth": None,
                "height": 10,
            },
            "collimator": {
                "width": 30,
                "depth": 30,
                "height": 65,
                "beam_height": 25.6,
                "beam_width": 1.0,
                "window": 0.2,
            },
        }
    elif source_type == "am_HS6":
        source = {
            "height": 0.1,
            "width": 1.0,
            "capsule": {
                "width": 11.08,
                "depth": 23.08,
                "height": 2.02,
            },
        }
    elif source_type == "co_HS5":
        source = {
            "height": 0.1,
            "width": 5.0,
            "foil": {"width": 20, "height": 0.5},
            "al_ring": {"height": 3.0, "width_max": 30, "width_min": 20},
        }
    elif source_type == "ba_HS4":
        source = {
            "height": 0.1,
            "width": 5.0,
            "foil": {
                "width": 26.0,
                "height": 0.5,
            },
            "al_ring": {"height": 3.0, "width_max": 30, "width_min": 26},
        }

    elif source_type == "th":
        source = {
            "height": 1.0,
            "width": 1.0,
            "capsule": {
                "height": 7.0,
                "width": 2.0,
            },
            "epoxy": {"height": 2.2, "width": 1.6},
            "plates": {"height": 2.0, "width": 8.0, "cavity_width": 2.0},
            "collimator": {
                "height": 30.0,
                "depth": 30.0,
                "width": 30.0,
                "beam_height": 15.0,
                "beam_width": 1.0,
            },
        }

        if meas_type == "top":
            source["offset_height"] = 0.0
        elif meas_type == "lat":
            source["offset_height"] = 18.0
        else:
            msg = "can only have top or lat measurements"
            raise RuntimeError(msg)
    else:
        msg = f"source type can only be am_HS1,  am_HS6, ba_HS4, co_HS5, am_HS6 or th_HS2 not {source_type}"
        raise RuntimeError(msg)

    return AttrsDict(source)


def get_source_holder(source_type, meas_type):
    if source_type in ["co_HS5", "ba_HS4", "am_HS1"]:
        source_holder["top"]["top_plate_height"] = 3.0
        source_holder["top"]["top_plate_width"] = 30.0
        source_holder["top"]["top_height"] = 10.0
        source_holder["top"]["top_inner_width"] = 20.0
        source_holder["top"]["top_bottom_height"] = 6.1
        source_holder["top"]["bottom_inner_width"] = 102.0

        source_holder["outer_width"] = 108.0
        source_holder["inner_width"] = 87.0

    elif source_type == "am_HS6":
        source_holder["outer_width"] = 108.0
        source_holder["inner_width"] = 87.0

        source_holder["am_HS6"]["top_height"] = 10.0
        source_holder["am_HS6"]["top_inner_width"] = 7.39
        source_holder["am_HS6"]["top_inner_depth"] = 15.39
        source_holder["am_HS6"]["bottom_inner_width"] = 102.0
        source_holder["am_HS6"]["top_bottom_height"] = 5.6
        source_holder["am_HS6"]["top_plate_width"] = 11.08
        source_holder["am_HS6"]["top_plate_depth"] = 23.08
        source_holder["am_HS6"]["top_plate_height"] = 2.0

    elif source_type == "th_HS2":
        source_holder["copper"]["height"] = 30.0
        source_holder["copper"]["height"] = 32.0
        source_holder["copper"]["cavity_width"] = 3.0
        source_holder["copper"]["bottom_height"] = 3.0
        source_holder["copper"]["bottom_width"] = 50.0

        if meas_type == "lat":
            source_holder["outer_width"] = 181.6
            source_holder["inner_width"] = 101.6
            source_holder["lat"]["height"] = 65.0
            source_holder["lat"]["cavity_height"] = 60.0
            source_holder["lat"]["cavity_width"] = 50.0
    else:
        msg = ""
        raise RuntimeError(msg)
