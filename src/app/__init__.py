import secrets
import os
from flask import Flask
from config import Config
from image_manager import ImageManager
from display_manager import DisplayManager
from refresh_manager import RefreshManager
from blueprints import (pidash, config, display, home, upload, gallery, settings)
from constants import (CONFIG_KEY, IMAGE_MANAGER_KEY, DISPLAY_MANAGER_KEY, REFRESH_MANAGER_KEY, HOSTNAME_KEY, LOCAL_IP_KEY)
from waitress import serve

def create_app(hostname=None):
    basedir = os.path.abspath(os.path.dirname(__file__))
    src_dir = os.path.dirname(basedir)
    app = Flask(__name__, template_folder=os.path.join(src_dir, "templates"), 
                static_folder=os.path.join(src_dir, "static"))
    
    app.secret_key = secrets.token_hex(16)

    configuration = Config()

    if hostname is not None:
        configuration.set(HOSTNAME_KEY, hostname)

    image_manager = ImageManager(configuration)
    display_manager = DisplayManager(configuration)
    refresh_manager = RefreshManager(configuration, image_manager, display_manager)

    app.config[CONFIG_KEY] = configuration
    app.config[IMAGE_MANAGER_KEY] = image_manager
    app.config[DISPLAY_MANAGER_KEY] = display_manager
    app.config[REFRESH_MANAGER_KEY] = refresh_manager

    app.register_blueprint(pidash.bp)
    app.register_blueprint(config.bp)
    app.register_blueprint(display.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(gallery.bp)
    app.register_blueprint(settings.bp)

    return app

if __name__ == "__main__":
    print("Starting PiDash webserver in development mode")
    app = create_app()
    serve(app, host="0.0.0.0", port=5000, threads=4)