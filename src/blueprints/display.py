from flask import (
    Blueprint, current_app, redirect, request, url_for
)

bp = Blueprint("display", __name__)

@bp.post("/refresh_screen")
def refresh_screen():
    try:
        current_app.config["refresh_manager"].refresh_display()
    except Exception:
        pass
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/show_next_image")
def show_next_image():
    try:
        current_app.config["refresh_manager"].display_next_image()
    except Exception:
        pass
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/show_previous_image")
def show_previous_image():
    try:
        current_app.config["refresh_manager"].display_previous_image()
    except Exception:
        pass
    return redirect(request.referrer or url_for("home.home"))

 