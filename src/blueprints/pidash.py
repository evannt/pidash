import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("pidash", __name__)

@bp.route("/")
def pidash():
    refresh_time = current_app.config["config"].get("refresh_interval")
    orientation = current_app.config["config"].get("orientation")
    images = current_app.config["image_manager"].get_image_names()
    current_image = images[0]

    return render_template("pidash.html",
                         current_image=current_image,
                         refresh_time=refresh_time,
                         orientation=orientation,
                         images=images)
