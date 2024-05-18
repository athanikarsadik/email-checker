#  For handling configuration settings
import json


def load_config(config_file="data/config.json", imap_file="data/imap_provider.json"):
    """Loads configuration settings from the specified JSON file.

    Args:
        config_file (str): Path to the configuration JSON file.
        imap_file (str): Path to the IMAP providers JSON file.

    Returns:
        dict: A dictionary containing the configuration settings.
    """

    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        config_data = {}  # Create an empty config if the file doesn't exist

    try:
        with open(imap_file, "r") as f:
            imap_providers = json.load(f)
    except FileNotFoundError:
        imap_providers = {}

    # Define default values for configuration settings
    config = {
        "imap_providers": imap_providers,
        "threads": config_data.get("threads", 1),
        "retry_attempts": config_data.get("retry_attempts", 3),
        "retry_timeout": config_data.get("retry_timeout", 5)
    }

    return config

def save_config(config, imap_file="data/imap_provider.json"):
    """Saves the configuration settings to the specified JSON file.

    Args:
        config (dict): The configuration settings to save.
        config_file (str): Path to the configuration JSON file.
        imap_file (str): Path to the IMAP providers JSON file.
    """

    with open(imap_file, "w") as f:
        json.dump(config["imap_providers"], f, indent=4)
