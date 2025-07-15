import secrets
from flask import Flask, render_template
from src.blueprints import display
from src.blueprints import pidash
from src.blueprints import config

def create_app():
    app = Flask(__name__)
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
