import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("pidash", __name__)

@bp.route("/")
def pidash():
    refresh_time = 900 # current_app.config["config"].get("refresh_interval")
    orientation = "horizontal" # current_app.config["config"].get("orientation")
    image_folder = os.path.abspath("src/static/images")
    images = [] #current_app.config["image_manager"].getImages()
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico'}

    for filename in os.listdir(image_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in image_extensions:
            images.append(filename)
    current_image = images[0]
    return render_template("pidash.html",
                         current_image=current_image,
                         refresh_time=refresh_time,
                         orientation=orientation,
                         images=images)
