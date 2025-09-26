import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("pidash", __name__)

@bp.route("/")
def pidash():
    cfg = current_app.config["config"]
    refresh_time = cfg.get("refresh_interval", 900)
    orientation = cfg.get("orientation", "landscape")
    images_dir = cfg.get("image_folder")

    image_folder = os.path.abspath(images_dir) if images_dir else os.path.abspath("src/static/images")
    try:
        from image_manager import ImageManager
        images = ImageManager.list_supported_images_in_dir(image_folder)
    except Exception:
        images = []

    current_image = images[0] if images else None

    return render_template("home.html",
                           current_image=current_image,
                           image_count=len(images),
                           refresh_time=refresh_time,
                           orientation=orientation,
                           images=images)
