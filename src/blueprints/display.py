from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint("display", __name__)

@bp.post("/refresh_screen")
def refresh_screen():
    current_app.config["refresh_manager"].refresh_display()
    return redirect(url_for("pidash.pidash"))

@bp.post("/show_next_image")
def show_next_image():
    current_app.config["refresh_manager"].display_next_image()
    return redirect(url_for("pidash.pidash"))

@bp.post("/show_previous_image")
def show_previous_image():
    current_app.config["refresh_manager"].display_previous_image()
    return redirect(url_for("pidash.pidash"))
