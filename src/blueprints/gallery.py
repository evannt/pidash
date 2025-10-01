import os
from flask import (
    Blueprint, current_app, render_template, request
)
from src.constants import (
    CONFIG_KEY, IMAGE_MANAGER_KEY, DEFAULT_GALLERY_LIMIT, CURRENT_IMAGE_INDEX_KEY
)

bp = Blueprint("gallery", __name__)

@bp.route("/gallery")
def home():
    config = current_app.config[CONFIG_KEY]
    image_manager = current_app.config[IMAGE_MANAGER_KEY]
    try:
        images = image_manager.get_image_names()
    except Exception:
        images = []

    show_all = request.args.get("all") == "1"
    current_index = config.get(CURRENT_IMAGE_INDEX_KEY)
    visible_images = images if show_all else images[current_index:current_index + min(DEFAULT_GALLERY_LIMIT, len(images))]
    current_image = image_manager.get_current_image_name()

    return render_template("gallery.html",
                           images=visible_images,
                           current_image=current_image,
                           total_count=len(images),
                           show_all=show_all,
                           gallery_limit=DEFAULT_GALLERY_LIMIT)