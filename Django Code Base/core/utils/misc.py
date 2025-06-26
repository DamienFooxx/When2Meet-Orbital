import yaml


def yaml_coerce(value):
    """
    Pass in a string to conver to a python dict
    """
    if isinstance(value, str):
        return yaml.load(f"dummy: {value}", Loader=yaml.SafeLoader)["dummy"]

    return value
