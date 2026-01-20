from __future__ import annotations

# Fixed Dimensions
# Base dimensions
BASE_WIDTH = 480.0
BASE_DEPTH = 450.0
BASE_HEIGHT = 500.0

# Inner cavity dimensions
INNER_CAVITY_WIDTH = 300.0
INNER_CAVITY_DEPTH = 250.0
INNER_CAVITY__HEIGHT = 500.0

# Cavity dimensions
CAVITY_WIDTH = 120.0
CAVITY_DEPTH = 100.0
CAVITY_HEIGHT = 400.0

# Top dimensions
TOP_WIDTH = 300.0
TOP_DEPTH = 300.0
TOP_HEIGHT = 90.0

# Front dimensions
FRONT_WIDTH = 160.0
FRONT_DEPTH = 100.0
FRONT_HEIGHT = 400.0

# Source holder dimensions
SOURCE_HOLDER_TOP_PLATE_HEIGHT = 3.0
SOURCE_HOLDER_TOP_PLATE_WIDTH = 30.0
SOURCE_HOLDER_TOP_HEIGHT = 10.0
SOURCE_HOLDER_TOP_INNER_WIDTH = 20.0
SOURCE_HOLDER_INNER_WIDTH = 87.0
SOURCE_HOLDER_BOTTOM_INNER_WIDTH = 102.0
SOURCE_HOLDER_OUTER_WIDTH = 108.0
SOURCE_HOLDER_TOPBOTTOM_HEIGHT = 6.1

# Source dimensions
SOURCE_HEIGHT = 0.1
SOURCE_WIDTH = 5.0

# Source foil
SOURCE_FOIL_HEIGHT = 0.5
SOURCE_FOIL_WIDTH = 26.0

# Aluminum ring around source
SOURCE_AL_RING_HEIGHT = 3.0
SOURCE_AL_RING_WIDTH_MAX = 30.0
SOURCE_AL_RING_WIDTH_MIN = 26.0

LEAD_CASTLE_1 = {
    "base_width": 480,
    "base_depth": 450,
    "base_height": 500,
    "inner_cavity_width": 300,
    "inner_cavity_depth": 250,
    "inner_cavity_height": 500,
    "cavity_width": 120,
    "cavity_depth": 100,
    "cavity_height": 400,
    "top_width": 300,
    "top_depth": 300,
    "top_height": 90,
    "front_width": 160,
    "front_depth": 100,
    "front_height": 400,
}

LEAD_CASTLE_2 = {
    "base_width": 350,
    "base_depth": 350,
    "base_height": 400,
    "inner_cavity_width": 250,
    "inner_cavity_depth": 250,
    "inner_cavity_height": 400,
    "top_width": 200,
    "top_depth": 200,
    "top_height": 50,
    "copper_plate_width": 350,
    "copper_plate_depth": 350,
    "copper_plate_height": 10,
}

BOTTOM_PLATE = {
    "width": 750,
    "depth": 750,
    "height": 15,
    "cavity_width": 120,
    "cavity_depth": 940,  # <!--475*2-->
    "cavity_height": 20,
}

# Cryostat dimensions
CRYOSTAT = {
    "height": 0,
    "width": 0,
    "thickness": 0,
    "position_cavity_from_top": 0,
    "position_cavity_from_bottom": 0,
    "position_from_bottom": 0,
}

# Changing relative dimensions
# Positions relative to cryostat initialise
POSITIONS_FROM_CRYOSTAT = {"detector": 0.0, "holder": 0.0, "wrap": 0.0}
POSITION_SOURCE_FROM_CRYOSTAT_PHI = 0.0
POSITION_SOURCE_FROM_CRYOSTAT_R = 0.0
POSITION_SOURCE_FROM_CRYOSTAT_X = 0.0
POSITION_SOURCE_FROM_CRYOSTAT_Y = -0.0
POSITION_SOURCE_FROM_CRYOSTAT_Z = 200.0


def update_cryostat_dims(hpge_meta):
    POSITIONS_FROM_CRYOSTAT["detector"] = hpge_meta["hades"]["dimensions"]["detector"]["position"]
    POSITIONS_FROM_CRYOSTAT["holder"] = hpge_meta["hades"]["dimensions"]["holder"]["position"]
    POSITIONS_FROM_CRYOSTAT["wrap"] = hpge_meta["hades"]["dimensions"]["wrap"]["position"]

    CRYOSTAT["position_cavity_from_top"] = 1.5
    CRYOSTAT["position_cavity_from_bottom"] = 0.8
    CRYOSTAT["position_from_bottom"] = 250.0
    CRYOSTAT["thickness"] = 1.5

    if hpge_meta["type"] == "bege":
        CRYOSTAT["height"] = 122.2
        CRYOSTAT["width"] = 101.6

    elif hpge_meta["type"] == "icpc":
        xl_orders = [3, 8, 9, 10]
        CRYOSTAT["height"] = 171.0
        if hpge_meta["production"]["order"] in xl_orders:
            CRYOSTAT["width"] = 114.3
        else:
            CRYOSTAT["width"] = 101.6

        if hpge_meta["production"]["order"] == 9 and hpge_meta["production"]["slice"] == "B":
            CRYOSTAT["width"] = 107.95
