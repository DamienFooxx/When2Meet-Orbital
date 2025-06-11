import os.path
from pathlib import Path
from split_settings.tools import include, optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Setting Base environment variables
ENVVAR_SETTINGS_PREFIX = "BASESETTINGS_"

include(
    'base.py',
    'custom.py',
    'templates/settings.dev.py',
    'envvars.py',
)