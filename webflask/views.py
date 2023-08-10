#!/usr/bin/python3
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from webflask.models import Image
from webflask import db


views = Blueprint('views', __name__)


@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    # Access the uploaded_images from the current app context
    uploaded_images = current_app.config['UPLOADED_IMAGES']

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

    return render_template('upload.html', user=current_user, username=current_user.username)
