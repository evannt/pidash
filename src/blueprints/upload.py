import os
from flask import (
    Blueprint, current_app, render_template, request, flash
)

bp = Blueprint("upload", __name__)

@bp.route("/upload")
def home():
    return render_template("upload.html")
