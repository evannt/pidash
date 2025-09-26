import secrets
import os
from flask import Flask, render_template
from blueprints import pidash
from blueprints import config
from blueprints import home
from blueprints import upload
from blueprints import gallery
from blueprints import settings
from blueprints import display
from config import Config

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    src_dir = os.path.dirname(basedir)
    app = Flask(__name__, template_folder=os.path.join(src_dir, "templates"), 
                static_folder=os.path.join(src_dir, "static"))
    app.secret_key = secrets.token_hex(16)

    real_config = Config()

    class DummyImageManager:
        def add_image(self, path):
            return True
        def remove_image(self, name):
            return True
        def remove_all_images(self):
            return True
        def set_current_image(self, name):
            return True

    class DummyRefreshManager:
        def refresh_display(self):
            return True
        def display_next_image(self):
            return True
        def display_previous_image(self):
            return True
        def start(self):
            return True
        def stop(self):
            return True

    # Inject real config and stubs so endpoints work as-is
    app.config["config"] = real_config
    app.config["image_manager"] = DummyImageManager()
    app.config["refresh_manager"] = DummyRefreshManager()

    # Register blueprints
    app.register_blueprint(pidash.bp)
    app.register_blueprint(config.bp)
    app.register_blueprint(display.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(gallery.bp)
    app.register_blueprint(settings.bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", debug=True)
