import os, pathlib, subprocess
from enum import Enum
from lib.parsing import reader

class Stages(Enum):
    Recipes    = "Recipes",
    BinPacking = "BPP",
    Layout     = "Layout"
    

class Config:
    def __init__(self):
        raise NotImplementedError("Instances of Config are not allowed")

    @classmethod
    def init(cls, root, cwd):

        if not os.path.isdir(root):
            raise ValueError(f"Invalid root directory {root}")

        if not os.path.isdir(cwd):
            cwd.mkdir(parents=True, exist_ok=True)
        
        cls.ROOT = root
        cls.CWD  = cwd

        cls.Recipes    = cls.__Stage(cls.ROOT, cls.CWD, "stage_1_recipes") 
        cls.BinPacking = cls.__Stage(cls.ROOT, cls.CWD, "stage_2_bpp")
        cls.Layout     = cls.__Stage(cls.ROOT, cls.CWD, "stage_3_layout")


    class __Stage:
        def __init__(self, root, cwd, stage_name):
            self.EPRIME   = (root / "model" / f"{stage_name}.eprime").resolve()
            self.PARAM    = (cwd / f"{stage_name}.param").resolve()
            self.SOLUTION = (cwd / f"{stage_name}.param.solution").resolve()

        def solution(self, n):
            return pathlib.Path(str(self.SOLUTION) + f".{n:06}")

        # Return (success, result) based on whether a solution was found
        def execute(self):
            subprocess.run([
                "savilerow",
                "-run-solver", "-chuffed",
                "-in-eprime", str(self.EPRIME),
                "-in-param", str(self.PARAM)
            ], cwd=str(Config.CWD))

            if not self.SOLUTION.is_file():
                return False, None

            with open(self.SOLUTION, "r") as f:
                return True, reader.parse(f)
