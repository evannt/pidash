import os
import tempfile
from flask import (
    Blueprint, current_app, flash, redirect, request, url_for
)
from werkzeug.utils import secure_filename

bp = Blueprint("config", __name__)

@bp.post("/update_config")
def update_config():
    has_errors = False

    if "refresh_interval" in request.form and "time_unit" in request.form:
        try:
            time_conversion_factor = 60
            if request.form["time_unit"] == "Hours":
                time_conversion_factor *= 60

            refresh_interval = int(request.form["refresh_interval"]) * time_conversion_factor
            prev_refresh_interval = current_app.config["config"].get("refresh_interval")
            if prev_refresh_interval != refresh_interval:
                current_app.config["config"].set("refresh_interval", refresh_interval, save=True)
            else:
                flash("Refresh time must be between 1 and 3600 seconds", "error")
                has_errors = True
        except (ValueError, TypeError):
            flash("Invalid refresh time - must be a number", "error")
            has_errors = True
    
    if "orientation" in request.form:
        orientation = request.form["orientation"]
        if orientation in ["landscape", "portrait"]:
            prev_orientation = current_app.config["config"].get("orientation")
            if prev_orientation != orientation:
                current_app.config["config"].set("orientation", orientation, save=True)
        else:
            flash("Invalid orientation - must be landscape or portrait", "error")
            has_errors = True

    if has_errors:
        flash("Some settings could not be updated due to errors", "error")
    
    current_app.config["refresh_manager"].refresh_display()

    return redirect(url_for("pidash.pidash"))

@bp.post("/upload_images")
def upload_images():
    files = request.files.getlist("image_upload_names")
    
    if not files or files[0].filename == "":
        flash("No files selected", "error")
        return redirect(url_for("pidash.pidash"))
    
    uploaded_count = 0
    
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                file.save(tmp_file.name)
                
                try:
                    current_app.config["image_manager"].add_image(tmp_file.name)
                    uploaded_count += 1
                except Exception as _:
                    flash(f"Failed to upload {filename}", "error")
                finally:
                    os.unlink(tmp_file.name)
    
    if uploaded_count > 0:
        flash(f"Uploaded {uploaded_count} image(s)", "success")
    
    return redirect(url_for("pidash.pidash"))

@bp.post("/remove_images")
def remove_images():
    image_names = request.form.get("removal_image_names", "").split(",")
    image_names = [name.strip() for name in image_names if name.strip()]
    
    if not image_names:
        flash("No images selected", "error")
        return redirect(url_for("pidash.pidash"))
    
    removed_count = 0
    
    for image_name in image_names:
        try:
            current_app.config["image_manager"].remove_image(image_name)
            removed_count += 1
        except Exception as _:
            flash(f"Failed to remove {image_name}", "error")
    
    if removed_count > 0:
        flash(f"Removed {removed_count} image(s)", "success")

    current_app.config["refresh_manager"].refresh_display()
    
    return redirect(url_for("pidash.pidash"))

@bp.post("/remove_all_images")
def remove_all_images():
    current_app.config["image_manager"].remove_all_images()
    return redirect(url_for("pidash.pidash"))

@bp.post("/change_current_image")
def change_current_image():
    image_name = request.form.get("current_image_name")

    if not image_name:
        flash("No image selected", "error")
        return redirect(url_for("pidash.pidash"))

    current_app.config["image_manager"].set_current_image(image_name)
    current_app.config["refresh_manager"].refresh_display()
    return redirect(url_for("pidash.pidash"))
