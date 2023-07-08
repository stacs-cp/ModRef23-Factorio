import numpy as np
from enum import Enum

class Types(Enum):
    INT = "integer"
    BOOL = "boolean"
    ARRAY = "array"
    MATRIX = "matrix"

    def __str__(self):
        return self.value


# Check if a decision variable matches the expected type and (for arrays and matrices) dimensions
def validate(value, expected_type: Types, expected_dims = None):
    if expected_type == Types.INT:
        return isinstance(value, int)

    if expected_type == Types.BOOL:
        return isinstance(value, bool)

    return isinstance(value, np.ndarray) and np.shape(value) == expected_dims
