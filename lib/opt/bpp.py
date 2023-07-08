import os
import numpy as np
from lib.utils.io import arr2str
from lib.utils.config import Config

def execute(dvars):
    # Generate parameters for the BPP model and execute it with Savile Row
    _generate_params(dvars["params"], dvars["recipes"])
    return Config.BinPacking.execute()


def _generate_params(params, recipes):
    # Merge input and output spaces to find all reserved spaces, then set each space's domain to int(0..1)
    reserved = np.add(params["input_qtys"], params["outputs"])
    reserved[reserved != 0] = 1

    # Ensure attempt arrays isn't empty
    attempts = np.array(params["bpp_assembler_attempts"])
    
    if params["bpp_attempts"] == 0:
        attempts = np.zeros(shape=(1, params["binW"] * params["binH"]), dtype=int)

    text = os.linesep.join([
        "language ESSENCE' 1.0",
        "",
        "$ Bin Size",
        f"letting binW = {params['binW']}",
        f"letting binH = {params['binH']}",
        "",
        "$ Layout",
        f"letting num_assemblers = {recipes['num_assemblers']}",
        f"letting inserters = {arr2str(recipes['inserters'][:recipes['num_assemblers']])}",
        f"letting reserved = {arr2str(reserved)}",
        "",
        "$ Previous solutions",
        f"letting num_attempts = {max(1, params['bpp_attempts'])}",
        f"letting attempts = {arr2str(attempts)}"
    ])

    # Create the param file in the given folder
    Config.BinPacking.PARAM.write_text(text)
