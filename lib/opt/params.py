import os
from lib.parsing import decisionvar as dv, reader

def read_params(param):
    if not os.path.isfile(param):
        raise ValueError("Invalid parameter file path provided")

    dvars = dict()

    # Read given params
    with open(param, "r") as f:
        dvars = reader.parse(f)
        
    _validate(dvars)

    # Generate some extra params
    dvars["max_assemblers"] = (dvars["binW"] // 3) * (dvars["binH"] // 3)

    dvars["total_attempts"] = 0

    dvars["recipe_attempts"] = 0
    dvars["recipe_assembler_attempts"] = []
    dvars["recipe_inserter_attempts"] = []

    dvars["bpp_attempts"] = 0
    dvars["bpp_assembler_attempts"] = []

    return dvars


def _validate(dvars):
    _validate_one(dvars, "binW",      dv.Types.INT)
    _validate_one(dvars, "binH",      dv.Types.INT)
    
    _validate_one(dvars, "num_items", dv.Types.INT)
    _validate_one(dvars, "out_item",  dv.Types.INT)

    _validate_one(dvars, "input_items",  dv.Types.MATRIX, (dvars["binH"], dvars["binW"]))
    _validate_one(dvars, "input_qtys",   dv.Types.MATRIX, (dvars["binH"], dvars["binW"]))
    _validate_one(dvars, "outputs",      dv.Types.MATRIX, (dvars["binH"], dvars["binW"]))

    _validate_one(dvars, "recipe_qtys",  dv.Types.MATRIX, (dvars["num_items"], dvars["num_items"]))
    _validate_one(dvars, "recipe_rates", dv.Types.ARRAY,  (dvars["num_items"],))

    _validate_one(dvars, "inserter_rate", dv.Types.INT)


def _validate_one(dvars, dvar, dvar_type, dimensions = None):
    if not dv.validate(dvars.get(dvar), dvar_type, dimensions):
        dim_msg = f" with dimensions {dimensions}" if dvar_type == dvar.Types.ARRAY or dvar_type == dvar.Types.MATRIX else ""
        raise ValueError(f"Expected parameter {dvar} to be of type {dvar_type}{dim_msg}, got {dvars.get(dvar)}")
