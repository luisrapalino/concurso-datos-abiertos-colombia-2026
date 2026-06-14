"""Approximate coordinates for territorial visualization (department centroids)."""

from shared.territorial import TerritorialCode

# Department-level centroids (lat, lng) keyed by two-digit DANE department code.
DEPARTMENT_CENTROIDS: dict[str, tuple[float, float]] = {
    "05": (6.2518, -75.5636),
    "08": (10.9639, -74.7964),
    "11": (4.7110, -74.0721),
    "13": (10.3910, -75.4794),
    "15": (5.5353, -73.3678),
    "17": (4.4389, -75.2322),
    "18": (1.6142, -75.6062),
    "19": (2.4448, -76.6147),
    "20": (9.2410, -75.2800),
    "23": (8.7479, -75.8814),
    "25": (4.8127, -75.7395),
    "27": (7.8939, -76.6302),
    "41": (2.9376, -75.2900),
    "44": (11.2408, -72.5880),
    "47": (10.4631, -73.2532),
    "50": (4.1420, -73.6268),
    "52": (1.2136, -77.2811),
    "54": (7.1193, -73.1227),
    "63": (4.5369, -75.6811),
    "66": (4.8133, -75.6961),
    "68": (7.1193, -73.1227),
    "70": (9.3040, -75.3978),
    "73": (4.4389, -75.2322),
    "76": (3.4516, -76.5320),
    "81": (7.0620, -70.7320),
    "85": (5.3470, -72.3950),
    "86": (1.1526, -76.6470),
    "88": (12.5847, -81.7006),
    "91": (-0.1866, -75.0150),
    "94": (6.1890, -67.4850),
    "95": (4.5709, -70.7578),
    "97": (1.2531, -70.2340),
    "99": (4.5709, -74.2973),
}

DEFAULT_COORDINATES = (4.5709, -74.2973)


def resolve_territorial_coordinates(territorial_code: TerritorialCode | str) -> tuple[float, float]:
    code = str(territorial_code).zfill(5)
    department_code = code[:2]
    return DEPARTMENT_CENTROIDS.get(department_code, DEFAULT_COORDINATES)
