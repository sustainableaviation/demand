import toml
from pathlib import Path

# Determine the current directory
current_directory = Path(__file__).resolve().parent


def get_api_key():
    config_path = current_directory / "config.toml"
    try:
        with open(config_path, "r") as config_file:
            config = toml.load(config_file)
            return config["api"]["key"]
    except FileNotFoundError:
        print("Config file not found!")
        return None
    except KeyError:
        print("API key not found in config file!")
        return None


api_key = get_api_key()

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}
