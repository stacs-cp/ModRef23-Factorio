import logging, sys
import numpy as np
from lib.utils.config import Config

def init(logname, level, save_to_file):
    logger = logging.getLogger(logname)
    logger.setLevel(level)

    # Create StreamHandler to output to console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)

    # Create FileHandler to output to file if requested
    if save_to_file:
        file = Config.CWD / f"{logname}.log"
        fh = logging.FileHandler(file)
        fh.setLevel(level)
        logger.addHandler(fh)

    return logger


def arr2str(arr):
    return np.array2string(arr, separator=', ', threshold=sys.maxsize)