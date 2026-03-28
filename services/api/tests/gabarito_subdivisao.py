RECTANGLE_POINTS = [
    {"x": 313500.0, "y": 7395000.0},
    {"x": 313800.0, "y": 7395000.0},
    {"x": 313800.0, "y": 7395400.0},
    {"x": 313500.0, "y": 7395400.0},
]

RECTANGLE_TOTAL_AREA = 120000.0

SUBDIVISION_CASES = {
    "area": {
        "area_alvo_m2": 60000.0,
        "expected_a": 60000.0,
        "expected_b": 60000.0,
    },
    "percentual": {
        "percentual": 30.0,
        "expected_a": 36000.0,
        "expected_b": 84000.0,
    },
    "vertice": {
        "indice_vertice": 0,
        "area_alvo_m2": 60000.0,
        "expected_a": 60000.0,
        "expected_b": 60000.0,
    },
    "ponto_fixo": {
        "ponto_fixo": {"x": 313650.0, "y": 7395200.0},
        "area_alvo_m2": 60000.0,
        "expected_a": 60000.0,
        "expected_b": 60000.0,
    },
}
