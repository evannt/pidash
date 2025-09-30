from flask import (
    Blueprint, current_app, redirect, request, url_for
)
from src.constants import REFRESH_MANAGER_KEY

bp = Blueprint("display", __name__)

@bp.route("/")
def home():
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/refresh_screen")
def refresh_screen():
    _refresh_display()
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/show_next_image")
def show_next_image():
    _refresh_display()
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/show_previous_image")
def show_previous_image():
    _refresh_display()
    return redirect(request.referrer or url_for("home.home"))

def _refresh_display():
    try:
        current_app.config[REFRESH_MANAGER_KEY].refresh_display()
    except Exception:
        pass