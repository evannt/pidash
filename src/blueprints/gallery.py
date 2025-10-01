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

    if show_all:
        visible_images = images
    else:
        total_images = len(images)
        window_size = DEFAULT_GALLERY_LIMIT
        
        half_window = window_size // 2
        start_index = max(0, current_index - half_window)
        end_index = min(total_images, start_index + window_size)
        
        if end_index - start_index < window_size:
            start_index = max(0, end_index - window_size)
        
        visible_images = images[start_index:end_index]

    current_image = image_manager.get_current_image_name()

    return render_template("gallery.html",
                           images=visible_images,
                           current_image=current_image,
                           total_count=len(images),
                           show_all=show_all,
                           gallery_limit=DEFAULT_GALLERY_LIMIT)