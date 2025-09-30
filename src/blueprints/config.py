import os
import tempfile
import magic
from PIL import Image
from flask import (
    Blueprint, current_app, flash, redirect, request, url_for
)
from werkzeug.utils import secure_filename
from src.constants import (
    MAX_FILE_SIZE_BYTES, ALLOWED_MIME_TYPES, SUPPORTED_IMAGE_EXTENSIONS,
    SECONDS_PER_MINUTE, SECONDS_PER_HOUR, ORIENTATION_KEY, REFRESH_INTERVAL_KEY,
    CONFIG_KEY, IMAGE_MANAGER_KEY, REFRESH_MANAGER_KEY
)
from src.validation import (
    ValidationError, validate_refresh_interval, validate_orientation
)

bp = Blueprint("config", __name__)

def validate_uploaded_file(file_path, filename):
    """Validate uploaded file for security and format."""
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            return False, f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB"
        
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in SUPPORTED_IMAGE_EXTENSIONS:
            return False, f"File type {file_ext} not allowed"

        mime = magic.from_file(file_path, mime=True)
        if mime not in ALLOWED_MIME_TYPES:
            return False, f"Invalid file format (detected: {mime})" 

        try:
            with Image.open(file_path) as img:
                img.verify()
            with Image.open(file_path) as img:
                img.load()
            return True, "File validation successful"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
            
    except Exception as e:
        return False, f"File validation error: {str(e)}"

@bp.post("/update_config")
def update_config():
    config = current_app.config[CONFIG_KEY]

    has_errors = False

    if "refresh_interval" in request.form and "time_unit" in request.form:
        try:
            value = int(request.form.get("refresh_interval"))
            unit = request.form.get("time_unit").lower()
            if unit == "hours":
                refresh_interval = value * SECONDS_PER_HOUR
            else:
                refresh_interval = value * SECONDS_PER_MINUTE
            
            validated_interval = validate_refresh_interval(refresh_interval)
            config.set(REFRESH_INTERVAL_KEY, validated_interval, save=True)
        except ValidationError as e:
            flash(str(e), "error")
            has_errors = True
        except (ValueError, TypeError):
            flash("Invalid refresh time - must be a number", "error")
            has_errors = True

    if "orientation" in request.form:
        try:
            validated_orientation = validate_orientation(request.form["orientation"])
            prev_orientation = config.get(ORIENTATION_KEY)
            if prev_orientation != validated_orientation:
                config.set(ORIENTATION_KEY, validated_orientation, save=True)
        except ValidationError as e:
            flash(str(e), "error")
            has_errors = True

    if has_errors:
        flash("Some settings could not be updated due to errors", "error")

    _refresh_display()

    return redirect(request.referrer or url_for("home.home"))

@bp.post("/upload_images")
def upload_images():
    config = current_app.config[CONFIG_KEY]
    image_manager = current_app.config[IMAGE_MANAGER_KEY]

    files = request.files.getlist("image_upload_names")
    
    if not files:
        flash("No files selected", "error")
        return redirect(request.referrer or url_for("home.home"))
    
    uploaded_count = 0
    rejected_count = 0
    
    for file in files:
        if file and file.filename:
            safe_filename = secure_filename(file.filename)
            tmp_path = None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
                tmp_path = tmp_file.name
                file.save(tmp_file.name)
                
                try:
                    is_valid, message = validate_uploaded_file(tmp_path, safe_filename)

                    if is_valid:
                        success = image_manager.add_image(tmp_path, safe_filename)
                        if success:
                            uploaded_count += 1
                        else:
                            flash(f"Failed to save {safe_filename}", "error")
                            rejected_count += 1
                    else:
                        flash(f"Rejected {safe_filename}: {message}", "error")
                        rejected_count += 1
                        
                except Exception as e:
                    flash(f"Failed to upload {safe_filename}: {str(e)}", "error")
                    rejected_count += 1
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except Exception:
                            pass
    
    if uploaded_count > 0:
        flash(f"Successfully uploaded {uploaded_count} image(s)", "success")
    if rejected_count > 0:
        flash(f"Rejected {rejected_count} file(s) due to security or format issues", "warning")
    
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/remove_images")
def remove_images():
    image_manager = current_app.config[IMAGE_MANAGER_KEY]

    image_names = request.form.get("removal_image_names", "").split(",")
    image_names = [name.strip() for name in image_names if name.strip()]
    
    if not image_names:
        flash("No images selected", "error")
        return redirect(url_for("home.home"))
    
    removed_count = 0
    
    for image_name in image_names:
        try:
            image_manager.remove_image(image_name)
            removed_count += 1
        except Exception as _:
            flash(f"Failed to remove {image_name}", "error")
    
    if removed_count > 0:
        flash(f"Removed {removed_count} image(s)", "success")

    _refresh_display()
    
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/remove_all_images")
def remove_all_images():
    current_app.config[IMAGE_MANAGER_KEY].remove_all_images()
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/change_current_image")
def change_current_image():
    image_name = request.form.get("current_image_name")

    if not image_name:
        flash("No image selected", "error")
        return redirect(request.referrer or url_for("home.home"))

    current_app.config[IMAGE_MANAGER_KEY].set_current_image(image_name)
    _refresh_display()

    return redirect(request.referrer or url_for("home.home"))

def _refresh_display():
    current_app.config[REFRESH_MANAGER_KEY].refresh_display()