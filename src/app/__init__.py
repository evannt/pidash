import secrets
from flask import Flask
from config import Config
from image_manager import ImageManager
from display_manager import DisplayManager
from refresh_manager import RefreshManager
from blueprints import pidash
from blueprints import config
from blueprints import display

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    configuration = Config()
    image_manager = ImageManager(configuration)
    display_manager = DisplayManager(configuration)
    refresh_manager = RefreshManager(configuration, image_manager, display_manager)

    app.config["config"] = configuration
    app.config["image_manager"] = image_manager
    app.config["display_manager"] = display_manager
    app.config["refresh_manager"] = refresh_manager

    app.register_blueprint(pidash.bp)
    app.register_blueprint(config.bp)
    app.register_blueprint(display.bp)

    return app
