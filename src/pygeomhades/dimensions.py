from __future__ import annotations

SOURCE_HOLDER = {
    "top_plate_height": 0.0,
    "top_plate_width": 0.0,
    "top_height": 0.0,
    "top_inner_width": 0.0,
    "inner_width": 0.0,
    "bottom_inner_width": 0.0,
    "outer_width": 0.0,
    "top_bottom_height": 0.0,
}

SOURCE = {
    "height": 0.0,
    "width": 0.0,
    "foil_height": 0.0,
    "foil_width": 0.0,
    "al_ring_height": 0.0,
    "al_ring_width_max": 0.0,
    "al_ring_width_min": 0.0,
}

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

LEAD_CASTLE = {}

BOTTOM_PLATE = {
    "width": 750,
    "depth": 750,
    "height": 15,
    "cavity_width": 120,
    "cavity_depth": 940,  # <!--475*2-->
    "cavity_height": 20,
}

CRYOSTAT = {
    "height": 0,
    "width": 0,
    "thickness": 0,
    "position_cavity_from_top": 0,
    "position_cavity_from_bottom": 0,
    "position_from_bottom": 0,
}

POSITIONS_FROM_CRYOSTAT = {
    "detector": 0.0,
    "holder": 0.0,
    "wrap": 0.0,
    "source": {"phi": 0.0, "r": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
}


def update_dims(hpge_meta: dict, config: dict) -> None:
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

    LEAD_CASTLE.clear()
    if config["lead_castle"] == 1:
        LEAD_CASTLE.update(LEAD_CASTLE_1)
    elif config["lead_castle"] == 2:
        LEAD_CASTLE.update(LEAD_CASTLE_2)
    else:
        msg = "only 2 lead castle options"
        raise RuntimeError(msg)
