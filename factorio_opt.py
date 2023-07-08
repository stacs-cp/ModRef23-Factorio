import argparse, logging, pathlib, webbrowser
import numpy as np
from datetime import datetime
from lib.utils import io, files
from lib.utils.config import Config, Stages
from lib.opt import params, bpp, recipes, layout
from lib.vis import renderer

OUTPUT_FOLDER  = "out"
LOGGING_PREFIX = "opt"


def main(args):
    # Read the given parameter file
    dvars = dict()
    dvars["args"] = args
    dvars["params"] = params.read_params(args.param)

    failed_at = None

    while dvars["params"]["recipe_attempts"] < args.max_recipes:
        # Choose a stage to run based on the stage the previous iteration failed at
        if failed_at == Stages.Recipes:
            raise ValueError("The desired output item cannot be created from the given parameters")

        elif failed_at == Stages.BinPacking or failed_at is None:        
            dvars, failed_at = run_recipes(dvars)

        elif failed_at == Stages.Layout:
            dvars, failed_at = run_bin_packing(dvars)

        # If no stages failed, a solution has been found
        if failed_at is None:
            # Visualise and save to a png file
            img = renderer.render_layout(dvars["layout"])
            path = str(Config.CWD / "solution.png")
            
            img.save(path)
            webbrowser.open(path)
            return

        # If this recipe has exceeded the allowed BPP attempts or run out of solutions, move on to the next one
        if (dvars["params"]["bpp_attempts"] >= args.max_bpp or repeat_solution(dvars["params"]["bpp_assembler_attempts"])):
            failed_at = None
            dvars["params"]["recipe_attempts"] += 1
            dvars["params"]["recipe_assembler_attempts"].append(dvars["recipes"]["assembler_recipes"])
            dvars["params"]["recipe_inserter_attempts"].append(dvars["recipes"]["inserters"])

        # If all valid recipe solutions have been tried, exit early
        if (repeat_solution(dvars["params"]["recipe_assembler_attempts"]) and repeat_solution(dvars["params"]["recipe_inserter_attempts"])):
            failed_at = Stages.Recipes

    raise ValueError("Failed to find a solution in the given number of attempts")


def run_recipes(dvars):
    success, dvars["recipes"] = recipes.execute(dvars)

    if not success:
        return dvars, Stages.Recipes

    dvars["recipes"]["inserters"] = np.sum(dvars["recipes"]["inserters_in"], axis=1) + dvars["recipes"]["inserters_out"]

    # Reset BPP attempts since a new recipe configuration is being used
    dvars["params"]["bpp_attempts"] = 0
    dvars["params"]["bpp_assembler_attempts"] = []
    
    return run_bin_packing(dvars)


def run_bin_packing(dvars):
    success, dvars["bpp"] = bpp.execute(dvars)

    if not success:
        files.cleanup(Config.Recipes)
        files.cleanup(Config.BinPacking)

        dvars["params"]["recipe_attempts"] += 1
        dvars["params"]["recipe_assembler_attempts"].append(dvars["recipes"]["assembler_recipes"])
        dvars["params"]["recipe_inserter_attempts"].append(dvars["recipes"]["inserters"])

        return dvars, Stages.BinPacking

    return run_layout(dvars)


def run_layout(dvars):
    success, dvars["layout"] = layout.execute(dvars)

    if not success:
        files.cleanup(Config.BinPacking)
        files.cleanup(Config.Layout)

        dvars["params"]["bpp_attempts"] += 1
        dvars["params"]["bpp_assembler_attempts"].append(dvars["bpp"]["assembler_layout"].flatten())

        return dvars, Stages.Layout

    return dvars, None


def repeat_solution(attempts):
    return len(attempts) > 1 and np.array_equal(attempts[-1], attempts[-2])


if __name__ == "__main__":
    # Take command line args
    argparser = argparse.ArgumentParser()

    argparser.add_argument("-p", "--param",       type=str, required=True)
    argparser.add_argument("-r", "--max-recipes", type=int, default=100)
    argparser.add_argument("-b", "--max-bpp",     type=int, default=100)
    argparser.add_argument("-k", "--keep-files",  action="store_true")
    argparser.add_argument("-s", "--save-log",    action="store_true")

    args = argparser.parse_args()

    # Set up folders
    root = pathlib.Path(__file__).parent
    subfolder = f"{pathlib.Path(args.param).stem}-{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}"
    cwd = root / OUTPUT_FOLDER / subfolder

    Config.init(root, cwd)
    
    # Initialise logging
    log = io.init(LOGGING_PREFIX, logging.INFO, args.save_log)

    # Main routine
    try:
        main(args)

    except ValueError as e:
        log.error(e)
        
    finally:
        if not args.keep_files:
            files.cleanup(Config.BinPacking)
            files.cleanup(Config.Recipes)
            files.cleanup(Config.Layout)
