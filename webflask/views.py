#!/usr/bin/env python3
import os
from datetime import datetime
from flask import (Blueprint, render_template, request,
                   flash, current_app, redirect, url_for)
from flask_login import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from werkzeug.utils import secure_filename
from sqlalchemy.orm import validates
from sqlalchemy import and_, func, desc
from webflask.models import User, Image, Auction, Bid
from webflask import db, create_app

views = Blueprint('views', __name__)


def mark_expired_auctions_as_deleted():
    # Create an app context
    app = create_app()
    app.app_context().push()

    # Now you can safely interact with the database and application context
    with app.app_context():
        # Get all expired but not deleted auctions
        expired_auctions = Auction.query.filter(
            Auction.end_time < datetime.utcnow(),
            Auction.deleted == False
        ).all()

        # Mark the auctions as deleted and commit the changes
        for auction in expired_auctions:
            auction.deleted = True

        db.session.commit()
        print('Scheduler task executed at:', datetime.now())


@views.route('/', methods=['GET', 'POST'])
def home_page():
    show_search = False
    show_div = True  # Set the value of show_div
    all_auctions = Auction.query.all()  # Fetch all auctions from all users
    last_bids = []  # Initialize last_bids as an empty list
    top_bids = []
    # auction_id = None
    # auction = None

    # if not current_user.is_anonymous:
    if current_user.is_authenticated:
        # Create a subquery to find the maximum timestamp per auction
        subquery = db.session.query(
            Bid.auction_id,
            func.max(Bid.timestamp).label('max_timestamp')
        ).filter(Bid.user_id == current_user.id
                 ).group_by(Bid.auction_id).subquery()

        # Use the subquery to find the last bids
        last_bids = db.session.query(Bid).join(
            Auction, Auction.id == Bid.auction_id
        ).join(
            subquery,
            and_(
                Bid.auction_id == subquery.c.auction_id,
                Bid.timestamp == subquery.c.max_timestamp
            )
        ).filter(Bid.user_id == current_user.id).all()

        # top_bids = db.session.query(Bid.user_id, Bid.auction_id, func.max(Bid.amount).label('max_bid')
        # ).group_by(Bid.user_id, Bid.auction_id).all()

        # Create a subquery to find the maximum bid amount per auction
        subquery = db.session.query(
            Bid.auction_id.label('auction_id'),
            func.max(Bid.amount).label('max_bid')
        ).group_by(Bid.auction_id).subquery()

        # Create another subquery to find the user who placed the maximum bid for each auction
        max_bid_users_subquery = db.session.query(
            Bid.auction_id.label('auction_id'),
            User.username.label('max_bid_username'),
            func.max(Bid.amount).label('max_bid')
        ).join(User, Bid.user_id == User.id).group_by(Bid.auction_id, User.username).subquery()

        # Join the subqueries to find the auction and the users who placed the maximum bids
        top_bids = db.session.query(
            Auction.id.label('auction_id'),
            max_bid_users_subquery.c.max_bid_username.label('username'),
            max_bid_users_subquery.c.max_bid.label('max_bid')
        ).join(
            max_bid_users_subquery,
            Auction.id == max_bid_users_subquery.c.auction_id
        ).order_by(desc(max_bid_users_subquery.c.max_bid)).limit(10).all()

    if request.method == 'POST':
        if current_user.is_authenticated:  # Check if the user is logged in
            # Process bid placement if a POST request is made
            bid_amount = request.form.get('amount')
            auction_id = request.form.get('auction_id')

            if bid_amount:
                try:
                    bid_amount = float(bid_amount)
                    auction = Auction.query.get(auction_id)

                    if auction and bid_amount >= auction.starting_bid:
                        bid = Bid(amount=bid_amount,
                                  user_id=current_user.id, auction_id=auction.id)
                        db.session.add(bid)
                        db.session.commit()
                        flash('Bid placed successfully!', category='success')
                        return redirect(url_for('views.home_page'))
                    else:
                        flash(
                            'Bid amount must be equal to or greater than the starting bid.', category='danger')
                except ValueError:
                    flash('Bid amount must be a valid number.', category='danger')
            else:
                flash('Bid amount is required.', category='danger')
        else:
            flash('You need to be logged in to place a bid.', category='danger')
            return redirect(url_for('auth.login'))

    return render_template("base.html", top_bids=top_bids, last_bids=last_bids,
                           show_search=show_search, show_div=show_div,
                           user=current_user, all_auctions=all_auctions)


@views.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    if current_user.is_admin:
        return redirect(url_for('views.admin_panel'))
    else:
        return redirect(url_for('views.user_admin_panel'))


@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    # Access the uploaded_images from the current app context
    uploaded_images = UploadSet(
        'images', IMAGES, default_dest=lambda app: app.config['UPLOADED_IMAGES_DEST'])

    auction = None  # Initialize the 'auction' variable

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        starting_bid = request.form.get('starting_bid')

        bid_amount = request.form.get('amount')

        image = request.files.getlist('image')

        # retrieve auction.id in the base.html for bids
        auction_id = request.form.get('auction_id')

        if title and description and start_time and end_time and starting_bid:
            if len(title) > 1 and len(description) > 1:
                # Validate the end time and starting bid
                @validates('end_time')
                def validate_end_time(end_time, start_time):
                    if end_time <= start_time:
                        raise ValueError("End time must be after start time.")
                    return end_time

                @validates('starting_bid')
                def validate_starting_bid(starting_bid):
                    starting_bid = float(starting_bid)
                    if starting_bid <= 0:
                        raise ValueError(
                            "Starting bid must be a positive value.")
                    return starting_bid

                # Convert form values to their appropriate data types
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
                starting_bid = float(starting_bid)

                try:
                    end_time = validate_end_time(end_time, start_time)
                    starting_bid = validate_starting_bid(starting_bid)
                except ValueError as e:
                    # Create a flash message for validation error
                    flash(str(e), 'danger')
                else:
                    # Handle the Auction form submission
                    # Create the Auction object and add it to the database
                    auction = Auction(title=title, description=description,
                                      start_time=start_time, end_time=end_time,
                                      starting_bid=starting_bid, user_id=current_user.id)
                    db.session.add(auction)
                    db.session.commit()
                    flash('Auction created successfully!', category='success')
            else:
                if len(title) <= 1:
                    flash('Title must be at least 2 characters long.',
                          category='danger')
                if len(description) <= 1:
                    flash('Description must be at least 2 characters long.',
                          category='danger')

            if end_time <= start_time:
                flash('End time must be after the start time.', category='danger')

            if float(starting_bid) <= 0:
                flash('Starting bid must be a positive value.', category='danger')

            if image:
                # Get a list of uploaded files
                for uploaded_file in image:
                    if uploaded_file:
                        # Sanitize the filename using secure_filename
                        filename = secure_filename(uploaded_file.filename)
                        # Save the sanitized filename
                        filename = uploaded_images.save(
                            uploaded_file, name=filename)

                        # Create an Image object and associate it with the current user and auction
                        if auction:
                            image = Image(
                                filename=filename, user_id=current_user.id, auction_id=auction.id)
                            db.session.add(image)
                            db.session.commit()
                            flash('Images submitted successfully!',
                                  category='success')
                        else:
                            flash(
                                'No active auction to associate images with!', category='danger')

        if bid_amount and bid_amount.isdigit() and auction_id:
            # Ensure bid_amount is a valid number
            try:
                bid_amount = float(bid_amount)
            except ValueError:
                flash('Bid amount must be a valid number.', category='danger')

            # Retrieve the associated auction's starting bid
            auction = Auction.query.get(auction_id)

            print("Retrieved auction_id:", auction_id)

            if auction:
                if bid_amount >= auction.starting_bid:
                    # if bid_amount is not None and starting_bid is not None and bid_amount >= starting_bid:
                    # Create a new Bid object associated with the auction
                    bid = Bid(amount=bid_amount, user_id=current_user.id,
                              auction_id=auction.id)
                    db.session.add(bid)
                    db.session.commit()
                    flash('Bid placed successfully!', category='success')
                else:
                    flash(
                        'Bid amount must be equal to or greater than the starting bid.', category='danger')
            else:
                flash('No active auction to place a bid!', category='danger')
        else:
            # flash('Invalid auction ID provided.', category='danger')
            flash(
                'Bid amount must be equal to or greater than the starting bid.', category='danger')

    all_auctions = Auction.query.all()  # Fetch all auctions from all users
    all_bids = Bid.query.all()

    return render_template('admin.html', user=current_user, username=current_user.username,
                           uploaded_images=uploaded_images, all_auctions=all_auctions,
                           all_bids=all_bids)


@views.route('/user-admin', methods=['GET', 'POST'])
@login_required
def user_admin_panel():
    # Access the uploaded_images from the current app context
    uploaded_images = UploadSet(
        'images', IMAGES, default_dest=lambda app: app.config['UPLOADED_IMAGES_DEST'])

    auction = None  # Initialize the 'auction' variable

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        starting_bid = request.form.get('starting_bid')

        bid_amount = request.form.get('amount')

        image = request.files.getlist('image')

        # retrieve auction.id in the base.html for bids
        auction_id = request.form.get('auction_id')

        if title and description and start_time and end_time and starting_bid:
            if len(title) > 1 and len(description) > 1:
                # Validate the end time and starting bid
                @validates('end_time')
                def validate_end_time(end_time, start_time):
                    if end_time <= start_time:
                        raise ValueError("End time must be after start time.")
                    return end_time

                @validates('starting_bid')
                def validate_starting_bid(starting_bid):
                    starting_bid = float(starting_bid)
                    if starting_bid <= 0:
                        raise ValueError(
                            "Starting bid must be a positive value.")
                    return starting_bid

                # Convert form values to their appropriate data types
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
                starting_bid = float(starting_bid)

                try:
                    end_time = validate_end_time(end_time, start_time)
                    starting_bid = validate_starting_bid(starting_bid)
                except ValueError as e:
                    # Create a flash message for validation error
                    flash(str(e), 'danger')
                else:
                    # Handle the Auction form submission
                    # Create the Auction object and add it to the database
                    auction = Auction(title=title, description=description,
                                      start_time=start_time, end_time=end_time,
                                      starting_bid=starting_bid, user_id=current_user.id)
                    db.session.add(auction)
                    db.session.commit()
                    flash('Auction created successfully!', category='success')
            else:
                if len(title) <= 1:
                    flash('Title must be at least 2 characters long.',
                          category='danger')
                if len(description) <= 1:
                    flash('Description must be at least 2 characters long.',
                          category='danger')

            if end_time <= start_time:
                flash('End time must be after the start time.', category='danger')

            if float(starting_bid) <= 0:
                flash('Starting bid must be a positive value.', category='danger')

            if image:
                # Get a list of uploaded files
                for uploaded_file in image:
                    if uploaded_file:
                        # Sanitize the filename using secure_filename
                        filename = secure_filename(uploaded_file.filename)
                        # Save the sanitized filename
                        filename = uploaded_images.save(
                            uploaded_file, name=filename)

                        # Create an Image object and associate it with the current user and auction
                        if auction:
                            image = Image(
                                filename=filename, user_id=current_user.id, auction_id=auction.id)
                            db.session.add(image)
                            db.session.commit()
                            flash('Images submitted successfully!',
                                  category='success')
                        else:
                            flash(
                                'No active auction to associate images with!', category='danger')

            # Retrieve the associated auction's starting bid
            auction = Auction.query.get(auction_id)

            print("Retrieved auction_id:", auction_id)

            if auction:
                if bid_amount >= auction.starting_bid:
                    # if bid_amount is not None and starting_bid is not None and bid_amount >= starting_bid:
                    # Create a new Bid object associated with the auction
                    bid = Bid(amount=bid_amount, user_id=current_user.id,
                              auction_id=auction.id)
                    db.session.add(bid)
                    db.session.commit()
                    flash('Bid placed successfully!', category='success')
                else:
                    flash(
                        'Bid amount must be equal to or greater than the starting bid.', category='danger')

    user_bids = Bid.query.filter_by(user_id=current_user.id).all()
    user_auctions = Auction.query.filter_by(user_id=current_user.id).all()

    return render_template('user_admin.html', user=current_user, username=current_user.username,
                           uploaded_images=uploaded_images, user_bids=user_bids,
                           user_auctions=user_auctions)


@views.route('/delete-auction/<int:id>', methods=['POST'])
@login_required
def delete_auction(id):
    auction = Auction.query.get(id)
    # auction = Auction.query.join(User).filter(User.is_admin == True, Auction.deleted == False).order_by(Auction.created_at.desc()).first()

    # Check if the auction exists and belongs to the current user & super delete for admin
    if current_user.is_admin or (auction and auction.user_id == current_user.id):
        # Get the associated images for this auction
        images = Image.query.filter_by(auction_id=id).all()

        # Delete the associated images from both the file system and the database
        for image in images:
            # Build the full path to the image file
            image_path = os.path.join(
                current_app.config['UPLOADED_IMAGES_DEST'], image.filename)
            if os.path.exists(image_path):
                os.remove(image_path)  # Delete the image file

        db.session.delete(auction)
        db.session.commit()
        return '', 204  # Return 'No Content' status for successful deletion
    else:
        return 'Unauthorized', 401  # Return 'Unauthorized' status
