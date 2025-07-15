import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("pidash", __name__)

@bp.route("/")
def pidash():
    refresh_time = 0 #current_app.config["config"].get("refresh_interval")
    orientation = "hello"#current_app.config["config"].get("orientation")
    images = []#current_app.config["image_manager"].get_image_names()
    current_image = None #current_app.config["image_manager"].get_current_image()

    return render_template("pidash.html",
                         current_image=current_image,
                         refresh_time=refresh_time,
                         orientation=orientation,
                         images=images)
