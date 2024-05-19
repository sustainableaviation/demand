# These code-snippets are re-used in many other files.
# They should be defined only once to avoid code duplication!

def get_api_key():
    try:
        with open("config.toml", "r") as config_file:
            config = toml.load(config_file)
            return config["api"]["key"]
    except FileNotFoundError:
        print("Config file not found!")
        return None
    except KeyError:
        print("API key not found in config file!")
        return None
    
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}
