#!/usr/bin/python3
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from werkzeug.utils import secure_filename
from webflask.models import User, Image, Auction, Bid
from webflask import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home_page():
    show_div = True  # Set the value of show_div
    return render_template("base.html", show_div=show_div, user=current_user)

# def get_appropriate_auction():
    # Select the last created auction based on the 'created_at' attribute (assuming it's a DateTime field)
    auction = Auction.query.filter(
        Auction.deleted is False  # Assuming you use a boolean field to mark auctions as deleted
    ).order_by(Auction.created_at.desc()).first()

    # If no active auction is found, you can create a new one or define your own logic.
    if auction is None:
        # Define your own logic here. For example, create a new auction or return None.
        pass

    print("Appropriate Auction:", auction)
    return auction


@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    # Access the uploaded_images from the current app context
    uploaded_images = UploadSet(
        'images', IMAGES, default_dest=lambda app: app.config['UPLOADED_IMAGES_DEST'])

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        starting_bid = request.form.get('starting_bid')

        bid_amount = request.form.get('amount')

        image = request.files.getlist('image')

        # Print the form data to the console for debugging
        print("Title:", title)
        print("Description:", description)
        print("Start Time:", start_time)
        print("End Time:", end_time)
        print("Starting Bid:", starting_bid)
        print("Bid Amount:", bid_amount)
        print("Images:", image)

        if title and description and start_time and end_time and starting_bid and bid_amount:
            # Handle the Auction form submission
            # Create the Auction object and add it to the database
            auction = Auction(title=title, description=description,
                              start_time=start_time, end_time=end_time,
                              starting_bid=starting_bid, user_id=current_user.id)
            db.session.add(auction)
            db.session.commit()
            flash('Auction created successfully!', category='success')

        if bid_amount:
            # Handle the Bid form submission
            bid_amount = float(bid_amount)

            def get_appropriate_auction():
                # Select the last created auction based on the 'created_at' attribute (assuming it's a DateTime field)
                auction = Auction.query.join(User).filter(User.is_admin == True, Auction.deleted == False).order_by(Auction.created_at.desc()).first()

                print("Appropriate Auction:", auction)
                return auction
            # Create the Bid object and add it to the database
            auction = get_appropriate_auction()  # Get the appropriate auction
            if auction:
                bid = Bid(amount=bid_amount, user_id=current_user.id,
                          auction_id=auction.id)
                db.session.add(bid)
                db.session.commit()
                flash('Bid placed successfully!', category='success')
            else:
                flash(
                    'No active auctions available. Create a new auction first.', category='error')

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
                    image = Image(
                        filename=filename, user_id=current_user.id, auction_id=auction.id)
                    db.session.add(image)
                    db.session.commit()
                    flash('Images submitted successfully!', category='success')
                else:
                    flash('No images selected!', category='error')

    return render_template('admin.html', user=current_user, username=current_user.username, uploaded_images=uploaded_images)
