import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("settings", __name__)

@bp.route("/settings")
def home():
    cfg = current_app.config["config"]
    refresh_time = cfg.get("refresh_interval", 900)
    orientation = cfg.get("orientation", "landscape")
    return render_template("settings.html", refresh_time=refresh_time, orientation=orientation)