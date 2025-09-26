import os
from flask import (
    Blueprint, current_app, render_template
)

bp = Blueprint("upload", __name__)

@bp.route("/upload")
def home():
    cfg = current_app.config["config"]
    images_dir = cfg.get("image_folder")
    max_upload_size = 10 * 1024 * 1024  # 10 MB default max upload size
    return render_template("upload.html", 
                         images_dir=images_dir,
                         max_upload_size=max_upload_size)