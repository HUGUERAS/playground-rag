INVERSE_CASE = {
    "start": {"name": "P1", "x": 313500.0, "y": 7395000.0},
    "end": {"name": "P2", "x": 313800.0, "y": 7395400.0},
    "expected": {
        "distancia": 500.0,
        "azimute_decimal": 36.869898,
        "azimute_dms": '36°52\'11.63"',
    },
}

AREA_CASE = {
    "points": [
        {"x": 313500.0, "y": 7395000.0},
        {"x": 313800.0, "y": 7395000.0},
        {"x": 313800.0, "y": 7395400.0},
        {"x": 313500.0, "y": 7395400.0},
    ],
    "expected": {
        "area_m2": 120000.0,
        "perimetro_m": 1400.0,
        "area_ha": 12.0,
    },
}

CONVERT_CASE = {
    "lat": -15.779167,
    "lon": -47.929722,
    "zona": "23S",
    "expected": {
        "este": 186085.106223,
        "norte": 8253307.867629,
        "srid": 31983,
    },
}
