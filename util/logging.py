from datetime import datetime
from pathlib import Path
import shutil

import logging

time = datetime.now().strftime("%y-%m-%d:%H-%M-%S")

ROOT = Path.cwd().joinpath(".logs")
LOG_DIR = ROOT.joinpath("current")
if LOG_DIR.exists():
    shutil.rmtree(LOG_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter("%(levelname)s-%(name)s-%(funcName)s-%(asctime)s - %(message)s")

class ZipFileHandler(logging.FileHandler):
    def __del__(self) -> None:
        print("TEST DEALLOC")

logging.getLogger().setLevel(logging.INFO)

def _set_module_logger(name: str, module: str|None) -> None:
    file_handler = ZipFileHandler(LOG_DIR.joinpath(f"_{name}_{time}.log"))
    file_handler.setFormatter(formatter)
    logger = logging.getLogger(module)
    logger.addHandler(file_handler)

_set_module_logger("all", None)
_set_module_logger("game", "game")   
_set_module_logger("objects", "objects")
_set_module_logger("registries", "registries")
_set_module_logger("util", "util")

