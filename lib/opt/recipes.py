import os
import numpy as np
from lib.utils.io import arr2str
from lib.utils.config import Config

def execute(dvars):
    # Generate parameters for the recipe model and execute it with Savile Row
    _generate_params(dvars["params"])
    return Config.Recipes.execute()


def _generate_params(params):
    # Find the total quantity of each item provided as input
    inputs = np.array([np.sum(params["input_qtys"][params["input_items"] == i + 1]) for i in range(params["num_items"])])

    # Ensure attempt arrays aren't empty
    assembler_attempts = np.array(params["recipe_assembler_attempts"])
    inserter_attempts = np.array(params["recipe_inserter_attempts"])
    
    if params["recipe_attempts"] == 0:
        assembler_attempts = np.zeros(shape=(1, params["max_assemblers"]), dtype=int)
        inserter_attempts = np.zeros(shape=(1, params["max_assemblers"]), dtype=int)

    text = os.linesep.join([
        "language ESSENCE' 1.0",
        "",
        "$ Bin Size",
        f"letting area = {params['binW'] * params['binH']}",
        "",
        "$ Assemblers",
        f"letting max_assemblers = {params['max_assemblers']}",
        "",
        "$ Inserters",
        f"letting inserter_rate = {params['inserter_rate']}",
        "",
        "$ Items",
        f"letting num_items = {params['num_items']}",
        f"letting inputs = {arr2str(inputs)}",
        f"letting output = {params['out_item']}",
        "",
        "$ Recipes",
        f"letting recipe_qtys = {arr2str(params['recipe_qtys'])}",
        f"letting recipe_rates = {arr2str(params['recipe_rates'])}",
        f"letting max_rate = {np.max(params['recipe_rates'])}",
        "",
        "$ Previous solutions",
        f"letting num_attempts = {max(1, params['recipe_attempts'])}",
        f"letting assembler_attempts = {arr2str(assembler_attempts)}",
        f"letting inserter_attempts = {arr2str(inserter_attempts)}"
    ])

    # Create the param file in the given folder
    Config.Recipes.PARAM.write_text(text)
