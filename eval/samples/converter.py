"""Medium: unit conversion with validation."""

CONVERSIONS = {
    ("celsius", "fahrenheit"): lambda c: c * 9 / 5 + 32,
    ("fahrenheit", "celsius"): lambda f: (f - 32) * 5 / 9,
    ("km", "miles"): lambda k: k * 0.621371,
    ("miles", "km"): lambda m: m / 0.621371,
    ("kg", "lbs"): lambda k: k * 2.20462,
    ("lbs", "kg"): lambda lb: lb / 2.20462,
}


def convert(value: float, from_unit: str, to_unit: str) -> float:
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    if from_unit == to_unit:
        return value

    key = (from_unit, to_unit)
    if key not in CONVERSIONS:
        raise ValueError(f"Unknown conversion: {from_unit} -> {to_unit}")

    return round(CONVERSIONS[key](value), 4)


def batch_convert(values: list[float], from_unit: str, to_unit: str) -> list[float]:
    return [convert(v, from_unit, to_unit) for v in values]
