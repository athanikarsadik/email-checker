#  For handling configuration settings
import json


def load_config(config_file="data/config.json"):
    """Loads configuration settings from the specified JSON file.

    Args:
        config_file (str): Path to the configuration JSON file.

    Returns:
        dict: A dictionary containing the configuration settings.
    """

    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        config_data = {}  # Create an empty config if the file doesn't exist

    # Define default values for configuration settings
    config = {
        "imap_providers": config_data.get("imap_providers", {}),
        "proxy": config_data.get("proxy", None),
        "threads": config_data.get("threads", 1),
        "retry_attempts": config_data.get("retry_attempts", 3),
        "retry_timeout": config_data.get("retry_timeout", 5)
    }

    return config

def save_config(config, config_file="data/config.json"):
    """Saves the configuration settings to the specified JSON file.

    Args:
        config (dict): The configuration settings to save.
        config_file (str): Path to the configuration JSON file.
    """

    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)