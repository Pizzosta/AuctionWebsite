#!/usr/bin/env python3

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "kawodze"
scheduler = APScheduler()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'whatyoudeemfit'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/' + DB_NAME

    # Configure connection pool and recycling for 1000 users
    #app.config['SQLALCHEMY_POOL_SIZE'] = 150
    #app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    #app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600 # Recycle connections after 1 hour of idle time

    # Directory for uploaded images
    app.config['UPLOADED_IMAGES_DEST'] = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'static/images/uploads')

    # Set up the upload directory and allowed extensions
    app.config['UPLOADED_IMAGES_ALLOW'] = IMAGES

    from webflask.views import datetime_local_format, current_datetime
    # Make the filter available to your Jinja2 environment
    app.jinja_env.filters['datetime_local_format'] = datetime_local_format
    app.jinja_env.globals['current_datetime'] = current_datetime

    # Set up the scheduler to check expired auctions
    if not scheduler.running:
        app.config['SCHEDULER_API_ENABLED'] = True
        scheduler.init_app(app)
        scheduler.start()

        # imported here to prevent circular import
        from webflask.views import mark_expired_auctions_as_deleted

        # Schedule the task to run every minute
        if not scheduler.get_job('mark_expired_auctions_job'):
            scheduler.add_job(
                id='mark_expired_auctions_job',
                func=mark_expired_auctions_as_deleted,
                trigger='interval',
                minutes=30
            )

    # Create the 'uploads' directory if it doesn't exist
    uploads_directory = app.config['UPLOADED_IMAGES_DEST']
    if not os.path.exists(uploads_directory):
        os.makedirs(uploads_directory)

    # Configure the upload sets
    uploaded_images = UploadSet('images', IMAGES)
    # Initialize the UploadSet with the app
    configure_uploads(app, uploaded_images)
    db.init_app(app)

    from webflask.views import views
    from webflask.auth import auth

    app.register_blueprint(views, url_prefix='/',
                           uploaded_images=uploaded_images)
    app.register_blueprint(auth, url_prefix='/')

    from webflask.models import User

    with app.app_context():
        db.create_all()
        print('Created Database!')

        # Create an admin user if not already present
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                firstname='Pizzosta',
                lastname='Ampah',
                username='Admin',
                email='admin@example.com',
                telephone='0243456789',
                password=generate_password_hash(
                    '1Admin_pass', method='scrypt'),
                agree=True,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print('Admin Created!')

        # Check if the user already exists
        existing_user1 = User.query.filter_by(email='1Pz@g.com').first()
        if not existing_user1:
            first_user = User(
                firstname='PZ',
                lastname='PZ',
                username='PZ',
                email='1Pz@g.com',
                telephone='+233243456788',
                password=generate_password_hash(
                    '1Pz@g.com', method='scrypt'),
                agree=True,
                is_admin=False
            )
            db.session.add(first_user)
            db.session.commit()
            print('First User Created!')

        # Check if the user already exists
        existing_user2 = User.query.filter_by(
            email='1John.doe@example.com').first()
        if not existing_user2:
            # If the user doesn't exist, create a new non-admin user
            second_user = User(
                firstname='John',
                lastname='Doe',
                username='NonAdminUser',
                email='1John.doe@example.com',
                telephone='+233243456787',
                password=generate_password_hash(
                    '1John.doe@example.com', method='scrypt'),
                agree=True,
                is_admin=False
            )
            db.session.add(second_user)
            db.session.commit()
            print('Second User created!')

        # Check if the first user already exists
        existing_user3 = User.query.filter_by(
            email='1Alice.johnson@example.com').first()
        if not existing_user3:
            # If the user doesn't exist, create a new non-admin user
            third_user = User(
                firstname='Alice',
                lastname='Johnson',
                username='User3',
                email='1Alice.johnson@example.com',
                telephone='+233243456786',
                password=generate_password_hash(
                    '1Alice.johnson@example.com', method='scrypt'),
                agree=True,
                is_admin=False
            )
            db.session.add(third_user)
            db.session.commit()
            print('Third User created!')

        # Check if the second user already exists
        existing_user4 = User.query.filter_by(
            email='1Bob.smith@example.com').first()
        if not existing_user4:
            # If the user doesn't exist, create a new non-admin user
            forth_user = User(
                firstname='Bob',
                lastname='Smith',
                username='User4',
                email='1Bob.smith@example.com',
                telephone='+233243456785',
                password=generate_password_hash(
                    '1Bob.smith@example.com', method='scrypt'),
                agree=True,
                is_admin=False
            )
            db.session.add(forth_user)
            db.session.commit()
            print('Forth User created!')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    login_manager.session_protection = 'strong'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
