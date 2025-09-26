import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("home", __name__)

@bp.route("/home")
def home():
    cfg = current_app.config["config"]
    refresh_time = cfg.get("refresh_interval", 900)
    orientation = cfg.get("orientation", "landscape")
    images_dir = cfg.get("image_folder")
    current_image_index = cfg.get("current_image_index", 0)

    # Use config value for image folder, fallback to hardcoded path for testing
    image_folder = os.path.abspath(images_dir) if images_dir else os.path.abspath("src/static/images")
    images = []

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico'}

    if os.path.isdir(image_folder):
        for filename in os.listdir(image_folder):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in image_extensions:
                images.append(filename)

    current_image = images[current_image_index] if images else None

    return render_template("home.html",
                           current_image=current_image,
                           image_count=len(images),
                           refresh_time=refresh_time,
                           orientation=orientation,
                           images=images)