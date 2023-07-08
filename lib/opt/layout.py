import os
import numpy as np
from lib.utils.io import arr2str
from lib.utils.config import Config

def execute(dvars):
    # Generate parameters for the recipe model and execute it with Savile Row
    _generate_params(dvars["params"], dvars["recipes"], dvars["bpp"])
    return Config.Layout.execute()


def _generate_params(params, recipes, bpp):
    text = os.linesep.join([
        "language ESSENCE' 1.0",
        "",
        "$ Bin Size",
        f"letting binW = {params['binW']}",
        f"letting binH = {params['binH']}",
        "",
        "$ Recipes",
        f"letting num_items = {params['num_items']}",
        f"letting recipes = {arr2str(params['recipe_qtys'])}",
        "",
        "$ Assemblers and inserters",
        f"letting num_assemblers = {recipes['num_assemblers']}",
        f"letting assembler_layout = {arr2str(bpp['assembler_layout'])}",
        f"letting assembler_recipes = {arr2str(recipes['assembler_recipes'][:recipes['num_assemblers']])}",
        f"letting inserters_in = {arr2str(recipes['inserters_in'][:recipes['num_assemblers']])}",
        f"letting inserters_out = {arr2str(recipes['inserters_out'][:recipes['num_assemblers']])}",
        "",
        "$ Input/output spaces",
        f"letting inputs = {arr2str(params['input_items'])}",
        f"letting outputs = {arr2str(params['outputs'])}",
        f"letting out_item = {params['out_item']}"
    ])

    # Create the param file in the given folder
    Config.Layout.PARAM.write_text(text)
