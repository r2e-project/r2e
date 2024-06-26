import os
from datetime import datetime
from pathlib import Path
import yaml

# Load configuration from config.yaml

current_dir = Path(__file__).parent
config_path = current_dir / "config.yml"
with open(config_path, "r") as file:
    config: dict[str, str] = yaml.safe_load(file)  # type: ignore

HOME_DIR = Path(os.path.expanduser("~"))
R2E_BUCKET_DIR = HOME_DIR / config["r2e_bucket_dir"]
REPOS_DIR = HOME_DIR / config["repos_dir"]
CACHE_DIR = HOME_DIR / config["cache_dir"]

GRAPHS_DIR = R2E_BUCKET_DIR / "repo_graphs"
INTERESTING_FUNCS_DIR = R2E_BUCKET_DIR / "interesting_functions"
TESTGEN_DIR = R2E_BUCKET_DIR / "testgen"
EXECUTION_DIR = R2E_BUCKET_DIR / "execution"
SPECGEN_DIR = R2E_BUCKET_DIR / "specgen"

EXTRACTED_DATA_DIR = R2E_BUCKET_DIR / "extracted_data"

CACHE_PATH = CACHE_DIR / "cache.json"
EXTRACTION_DIR = R2E_BUCKET_DIR / "extracted_data"

PDM_BIN_DIR = "/home/naman_jain/.local/bin:$PATH"


# HELPER FUNCTIONS


def timestamp() -> str:
    """Return the current timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
