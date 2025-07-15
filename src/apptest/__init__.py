import secrets
import os
from flask import Flask, render_template
from blueprints import display
from blueprints import pidash
from blueprints import config

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    src_dir = os.path.dirname(basedir)
    app = Flask(__name__, template_folder=os.path.join(src_dir, "templates"), 
                static_folder=os.path.join(src_dir, "static"))
    app.secret_key = secrets.token_hex(16)
    app.register_blueprint(pidash.bp)
    app.register_blueprint(config.bp)
    app.register_blueprint(display.bp)

    @app.route("/")
    def test():
        return render_template("pidash.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", debug=True)
