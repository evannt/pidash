import os
import tempfile
from PIL import Image

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
from flask import (
    Blueprint, current_app, flash, redirect, request, url_for
)
from werkzeug.utils import secure_filename
from src.constants import (
    MAX_FILE_SIZE_BYTES, ALLOWED_MIME_TYPES, SUPPORTED_IMAGE_EXTENSIONS,
    MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL, VALID_ORIENTATIONS,
    SECONDS_PER_MINUTE, SECONDS_PER_HOUR
)
from src.validation import (
    ValidationError, validate_refresh_interval, validate_orientation,
    sanitize_filename, validate_image_settings
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
        
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_file(file_path, mime=True)
                if mime_type not in ALLOWED_MIME_TYPES:
                    return False, f"MIME type {mime_type} not allowed"
            except Exception:
                pass
        
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True, "File validation successful"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
            
    except Exception as e:
        return False, f"File validation error: {str(e)}"

@bp.post("/update_config")
def update_config():
    has_errors = False

    if "refresh_time" in request.form and "time_unit" in request.form:
        try:
            value = int(request.form.get("refresh_time", "0"))
            unit = request.form.get("time_unit", "minutes").lower()
            if unit == "hours":
                refresh_interval = value * SECONDS_PER_HOUR
            else:
                refresh_interval = value * SECONDS_PER_MINUTE
            
            validated_interval = validate_refresh_interval(refresh_interval)
            current_app.config["config"].set("refresh_interval", validated_interval, save=True)
        except ValidationError as e:
            flash(str(e), "error")
            has_errors = True
        except (ValueError, TypeError):
            flash("Invalid refresh time - must be a number", "error")
            has_errors = True

    if "orientation" in request.form:
        try:
            orientation = request.form["orientation"]
            validated_orientation = validate_orientation(orientation)
            prev_orientation = current_app.config["config"].get("orientation")
            if prev_orientation != validated_orientation:
                current_app.config["config"].set("orientation", validated_orientation, save=True)
        except ValidationError as e:
            flash(str(e), "error")
            has_errors = True

    if has_errors:
        flash("Some settings could not be updated due to errors", "error")

    current_app.config["refresh_manager"].refresh_display()

    return redirect(request.referrer or url_for("home.home"))

@bp.post("/upload_images")
def upload_images():
    files = request.files.getlist("image_upload_names")
    
    if not files or files[0].filename == "":
        flash("No files selected", "error")
        return redirect(request.referrer or url_for("home.home"))
    
    uploaded_count = 0
    rejected_count = 0
    
    for file in files:
        if file and file.filename:
            try:
                filename = sanitize_filename(file.filename)
                secure_name = secure_filename(filename)
                if secure_name != filename:
                    flash(f"Filename contains unsafe characters: {filename}", "error")
                    rejected_count += 1
                    continue
            except ValidationError as e:
                flash(f"Invalid filename: {str(e)}", "error")
                rejected_count += 1
                continue
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                file.save(tmp_file.name)
                
                try:
                    is_valid, message = validate_uploaded_file(tmp_file.name, filename)
                    
                    if is_valid:
                        current_app.config["image_manager"].add_image(tmp_file.name)
                        uploaded_count += 1
                    else:
                        flash(f"Rejected {filename}: {message}", "error")
                        rejected_count += 1
                        
                except Exception as e:
                    flash(f"Failed to upload {filename}: {str(e)}", "error")
                    rejected_count += 1
                finally:
                    try:
                        os.unlink(tmp_file.name)
                    except Exception:
                        pass
    
    if uploaded_count > 0:
        flash(f"Successfully uploaded {uploaded_count} image(s)", "success")
    if rejected_count > 0:
        flash(f"Rejected {rejected_count} file(s) due to security or format issues", "warning")
    
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/remove_images")
def remove_images():
    image_names = request.form.get("removal_image_names", "").split(",")
    image_names = [name.strip() for name in image_names if name.strip()]
    
    if not image_names:
        flash("No images selected", "error")
        return redirect(url_for("home.home"))
    
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
    
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/remove_all_images")
def remove_all_images():
    current_app.config["image_manager"].remove_all_images()
    return redirect(request.referrer or url_for("home.home"))

@bp.post("/change_current_image")
def change_current_image():
    image_name = request.form.get("current_image_name")

    if not image_name:
        flash("No image selected", "error")
        return redirect(request.referrer or url_for("home.home"))

    current_app.config["image_manager"].set_current_image(image_name)
    current_app.config["refresh_manager"].refresh_display()
    return redirect(request.referrer or url_for("home.home"))
