#!/usr/bin/python3
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_uploads import UploadSet, configure_uploads
from werkzeug.utils import secure_filename
from webflask.models import Image
from webflask import db


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home_page():
    show_div = True  # Set the value of show_div
    return render_template("base.html", show_div=show_div, user=current_user)


@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    # Access the uploaded_images from the current app context
    uploaded_images = current_app.config['UPLOADED_IMAGES_DEST']

    if request.method == 'POST' and 'image' in request.files:
        uploaded_file = request.files['image']
        if uploaded_file:
            # Sanitize the filename using secure_filename
            filename = secure_filename(uploaded_file.filename)
            # Save the sanitized filename
            filename = uploaded_images.save(uploaded_file, name=filename)

            # Create an Image object and associate it with the current user
            image = Image(filename=filename, user_id=current_user.id)
            db.session.add(image)
            db.session.commit()
            flash('Images submitted successfully!', category='success')
        else:
            flash('No images selected!', category='error')

    return render_template('admin.html', user=current_user, username=current_user.username)
