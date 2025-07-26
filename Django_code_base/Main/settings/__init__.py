from pathlib import Path
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Setting Base environment variables
ENVVAR_SETTINGS_PREFIX = "BASESETTINGS_"

include(
    "base.py",
    "connections.py",
    "applications.py",
    "envvars.py",
)
