import numpy as np

def std(values: list[float]) -> float:
    return float(np.std(values)) if values else 0.0