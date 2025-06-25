from core.utils.collections import deep_update
from core.utils.settings import get_settings_from_environment
from Main.settings import ENVVAR_SETTINGS_PREFIX

"""
Look for envvars with a specific prefix and strip out the prefix to be used as global envvars
"""

deep_update(globals(), get_settings_from_environment(ENVVAR_SETTINGS_PREFIX))
