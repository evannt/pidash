import os
from src.config import Config

def test_config_file_exists():
    config = Config()

    assert os.path.exists(config.config_file)

def test_config_loads():
    config = Config()

    assert config.config_file is not None
    assert config.config is not None

def test_default_config_loads():
    config = Config()

    assert config.get("name") == "PiDash"
    assert config.get("image_folder") == "src/static/images"
    assert config.get("orientation") == "landscape"
    assert config.get("inverted_image") == False
    assert config.get("refresh_interval") == 900
    assert config.get("startup") == True
    assert config.get("current_image_index") == 0
    assert config.get("image_settings") == {
        "brightness": 1.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "sharpness": 1.0
    }

def test_config_sets():
    config = Config()

    assert config.get("orientation") == "landscape"
    config.set("orientation", "portrait", save=False)
    assert config.get("orientation") == "portrait"

def test_config_sets_new_value():
    config = Config()

    assert config.get("new_key") is None
    config.set("new_key", "new_value", save=False)
    assert config.get("new_key") == "new_value"