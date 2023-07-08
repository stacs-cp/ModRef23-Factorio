import re
import numpy as np

decision_vars = re.compile(r"letting\s+(\w+)\s+(=|be)\s+")
eprime_bool   = re.compile(r"(false|true)")
eprime_int    = re.compile(r"(-?\d+)")


# Parse an Essence Prime solution file
def parse(file):
    # Ensure the first line is an Essence' language statement
    lang_spec = file.readline()

    if not lang_spec == "language ESSENCE' 1.0\n":
        raise ValueError("Solution file is not a valid Essence' file")

    return _parse_decision_vars(file)


# Parse each decision variable definition in a solution file
def _parse_decision_vars(file):
    n = 1
    dvars = dict()
    
    dvar = ""
    value = ""

    for line in file:
        # Track line number for better error messages
        n += 1

        # Check if the line defines a decision variable
        new_dvar = decision_vars.match(line)

        if new_dvar:
            # The current dvar is completely read, parse its value
            if dvar:
                dvars[dvar] = _parse_value(value)

            # Capture the new dvar's name and any value specified on this line
            dvar = new_dvar.group(1)
            value = decision_vars.sub("", line).split("$", 1)[0].strip()

        else:
            # Read the next line of the current dvar
            value += line.split("$", 1)[0].strip()

    # Capture the last decision variable
    if dvar:
        dvars[dvar] = _parse_value(value)

    return dvars


# Given an Essence Prime variable value, parse it as the correct data type
def _parse_value(value):
    depth = len(value) - len(value.lstrip("["))

    # int or bool
    if depth == 0:
        return _parse_primitive(value)

    # array
    elif depth == 1:
        return np.array(_parse_array(value))

    
    # matrix
    elif depth >= 2:
        return np.array(_parse_matrix(value, depth))

    # Invalid format
    raise ValueError(f"Invalid decision variable format: {value}")


# Given a primitive, parse it as the correct data type
def _parse_primitive(value):
    # bool
    is_bool = eprime_bool.match(value)
    
    if is_bool:
        return is_bool.group(1) == "true"

    # int
    is_int = eprime_int.match(value)

    if is_int:
        return int(is_int.group(1))

    # Invalid format
    raise ValueError(f"Invalid decision variable format: {value}")


# Given a 1D array, parse the values within it
def _parse_array(arr):
    values = arr.strip("[]").partition(";")[0].split(",")
    return [_parse_primitive(v.strip()) for v in values]


# Given an n-dimensional matrix, parse the values within it
def _parse_matrix(matrix, depth):
    # Only parse for 2D matrices or higher
    if depth < 2:
        raise ValueError("parse_matrix is for n-dimensional matrices where n >= 2")
        
    # Base case: parse the rows of a 2D matrix
    if depth == 2:
        rows = re.split(r"]\s*,\s*\[", matrix)
        return [_parse_array(row) for row in rows]

    # Recursive case: decrease depth by one
    else:
        depth -= 1

        pattern = r"]\s*,\s*" + (r"\[" * depth)
        submatrices = re.split(pattern, matrix)

        return [_parse_matrix(submatrix, depth) for submatrix in submatrices]
