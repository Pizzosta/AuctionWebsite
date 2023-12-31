#!/usr/bin/env python3
from datetime import datetime
from sqlalchemy.orm import validates
from flask_login import UserMixin
from webflask import db


class User(db.Model, UserMixin):
    # __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(13), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    agree = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)  # Soft delete column

    # Define a one-to-many relationship with auctions (one user can create multiple auctions)
    auctions = db.relationship(
        'Auction', backref='user', lazy=True, cascade='all, delete-orphan')

    # Define a one-to-many relationship with bids (one user can place multiple bids)
    bids = db.relationship('Bid', backref='user', lazy=True)

    # Define a one-to-many relationship with bids (one user can be associated with multiple images)
    images = db.relationship('Image', backref='user', lazy=True)

    @validates('firstname', 'lastname', 'username', 'email')
    def validate_not_empty(self, key, value):
        if not value:
            raise ValueError(f"{key.capitalize()} cannot be empty.")
        return value


class Auction(db.Model):
    # __tablename__ = 'Auction'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    start_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #starting_bid = db.Column(db.Float, nullable=False)
    starting_bid = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    deleted = db.Column(db.Boolean, default=False)  # Soft delete column

    # Define a many-to-one relationship with users (many auctions can be created by one user)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a one-to-many relationship with bids (one auction can have multiple bids)
    bids = db.relationship('Bid', backref='auction',
                           lazy=True, cascade='all, delete-orphan')

    # Define a one-to-many relationship with images (one auction can have multiple images)
    images = db.relationship('Image', backref='auction',
                             lazy=True, cascade='all, delete-orphan')


class Bid(db.Model):
    # __tablename__ = 'Bid'
    id = db.Column(db.Integer, primary_key=True)
    #amount = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    deleted = db.Column(db.Boolean, default=False)  # Soft delete column
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Define a many-to-one relationship with users (many bids can be placed by one user)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a many-to-one relationship with auctions (many bids can be placed on one auction)
    auction_id = db.Column(db.Integer, db.ForeignKey(
        'auction.id', ondelete='CASCADE'), nullable=False)


class Image(db.Model):
    # __tablename__ = 'Image'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), nullable=False)
    deleted = db.Column(db.Boolean, default=False)  # Soft delete column

    # Define a many-to-one relationship with auctions (many images can belong to one auction)
    auction_id = db.Column(db.Integer, db.ForeignKey(
        'auction.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Image(id={self.id}, filename='{self.filename}')"
