import os
from flask import (
    Blueprint, current_app, render_template
)
from src.constants import (
    CONFIG_KEY, REFRESH_INTERVAL_KEY, ORIENTATION_KEY, IMAGE_MANAGER_KEY, IMAGE_FOLDER_KEY
)

bp = Blueprint("pidash", __name__)

@bp.route("/")
def pidash():
    cfg = current_app.config[CONFIG_KEY]
    refresh_time = cfg.get(REFRESH_INTERVAL_KEY)
    orientation = cfg.get(ORIENTATION_KEY)
    images_dir = cfg.get(IMAGE_FOLDER_KEY)

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
