import os
from flask import (
    Blueprint, current_app, render_template, request
)

bp = Blueprint("gallery", __name__)

@bp.route("/gallery")
def home():
    cfg = current_app.config["config"]
    orientation = cfg.get("orientation")
    refresh_interval = cfg.get("refresh_interval")
    images_dir = cfg.get("image_folder")

    image_folder = os.path.abspath(images_dir) if images_dir else os.path.abspath("src/static/images")
    try:
        from image_manager import ImageManager
        images = ImageManager.list_supported_images_in_dir(image_folder)
    except Exception:
        images = []

    show_all = request.args.get("all") == "1"
    initial_limit = 24
    visible_images = images if show_all else images[:initial_limit]

    current_image = images[0] if images else None
    return render_template("gallery.html",
                           images=visible_images,
                           current_image=current_image,
                           total_count=len(images),
                           show_all=show_all,
                           initial_limit=initial_limit)