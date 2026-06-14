from shared.colombia_coordinates import resolve_territorial_coordinates


def test_resolve_territorial_coordinates_uses_divipola_municipality() -> None:
    latitude, longitude = resolve_territorial_coordinates("05001")
    assert 6.0 < latitude < 6.5
    assert -76.0 < longitude < -75.0
