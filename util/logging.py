from datetime import datetime
from pathlib import Path
import shutil
import tarfile
import logging

time = datetime.now().strftime("%y-%m-%d:%H-%M-%S")

ROOT = Path.cwd().joinpath(".logs")
LOG_DIR = ROOT.joinpath("current")
if LOG_DIR.exists():
    shutil.rmtree(LOG_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter("%(levelname)s - %(name)s:%(funcName)s - %(asctime)s - %(message)s")


logging.getLogger().setLevel(logging.INFO)


def _set_module_logger(name: str, module: str | None) -> None:
    file_handler = logging.FileHandler(LOG_DIR.joinpath(f"_{name}_{time}.log"))
    file_handler.setFormatter(formatter)
    logger = logging.getLogger(module)
    logger.addHandler(file_handler)


_set_module_logger("all", None)
_set_module_logger("main", "main")
_set_module_logger("game", "game")
_set_module_logger("objects", "objects")
_set_module_logger("registries", "registries")
_set_module_logger("util", "util")

logger = logging.getLogger(__name__)


def zip_logs():
    arc_dir = ROOT.joinpath(f"{time}.tar.gz")
    logger.info(f"Creating log tar {arc_dir}")
    file = tarfile.open(arc_dir, "w:gz")
    for log in LOG_DIR.glob("*"):
        file.add(log)
    file.close()
