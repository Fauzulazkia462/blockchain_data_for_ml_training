from collections import Counter

def most_common(values: list[float]) -> float:
    if not values:
        return 0.0
    (value, _), *_ = Counter(values).most_common(1)
    return value