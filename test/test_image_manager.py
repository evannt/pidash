import os
from src.constants import HOSTNAME_KEY, LOCAL_IP_KEY
from src.config import Config
from src.image_manager import ImageManager

def test_image_manager_loads():
    config = Config()
    config.set(HOSTNAME_KEY, "Hello Pidash!")
    config.set(LOCAL_IP_KEY, "This is sub text")
    _ = ImageManager(config=config)

def test_create_image():
    config = Config()
    config.set(HOSTNAME_KEY, "Hello Pidash!")
    config.set(LOCAL_IP_KEY, "This is sub text")

    assert config.get(HOSTNAME_KEY) == "Hello Pidash!"
    assert config.get(LOCAL_IP_KEY) == "This is sub text"

    image_manager = ImageManager(config=config)

    default_landscape = image_manager.default_image_landscape_path
    default_portrait = image_manager.default_image_portrait_path

    assert default_landscape is not None
    assert default_portrait is not None

    assert os.path.exists(default_landscape)
    assert os.path.exists(default_portrait)

    default_landscape_name = os.path.basename(default_landscape)
    default_portrait_name = os.path.basename(default_portrait)

    assert default_landscape_name == "default_landscape.png"
    assert default_portrait_name == "default_portrait.png"

    assert "default_landscape.png" not in image_manager.get_image_names()
    assert "default_portrait.png" not in image_manager.get_image_names()

    os.remove(default_landscape)
    os.remove(default_portrait)

    del config.config[HOSTNAME_KEY]
    del config.config[LOCAL_IP_KEY]
    config.save_config()
