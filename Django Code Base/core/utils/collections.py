def deep_update(base_dict, update_with):
    # Iterate over each item in the new dict
    for key, value in update_with.items():
        # If the value is a dict
        if isinstance(value, dict):
            base_dict_value = base_dict.get(key)
            # If the original value is also a dict then recurse through this function again
            if isinstance(base_dict_value, dict):
                deep_update(base_dict_value, value)
            # If not a dict then set as new value
            else:
                base_dict[key] = value
        # If the new value is not a dict
        else:
            base_dict[key] = value
    return base_dict
