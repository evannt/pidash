from flask import (
    Blueprint, current_app, render_template
)
from src.constants import (
    CONFIG_KEY, REFRESH_INTERVAL_KEY, ORIENTATION_KEY, IMAGE_MANAGER_KEY
)

bp = Blueprint("home", __name__)

@bp.route("/home")
def home():
    config = current_app.config[CONFIG_KEY]
    image_manager = current_app.config[IMAGE_MANAGER_KEY]
    refresh_time = config.get(REFRESH_INTERVAL_KEY)
    orientation = config.get(ORIENTATION_KEY)

    image_count = image_manager.get_image_count()
    current_image = image_manager.get_current_image_name()

    return render_template("home.html",
                           current_image=current_image,
                           image_count=image_count,
                           refresh_time=refresh_time,
                           orientation=orientation)
                           