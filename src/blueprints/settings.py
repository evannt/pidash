import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("settings", __name__)

@bp.route("/settings")
def home():
    cfg = current_app.config["config"]
    refresh_interval = cfg.get("refresh_interval")
    orientation = cfg.get("orientation")

    return render_template("settings.html",
                           refresh_interval=refresh_interval,
                           orientation=orientation)