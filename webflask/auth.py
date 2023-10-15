import re 
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from webflask.models import User
from webflask import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home_page'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if user.is_admin:
                    return redirect(url_for('views.admin_panel'))
                else:
                    return redirect(url_for('views.home_page'))
            else:
                flash('Incorrect password, try again', category='danger')
        else:
            flash('Email not found! Try creating an account first.', category='danger')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    show_div = True
    # return redirect(url_for('auth.login'))
    return render_template("base.html", show_div=show_div, user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        error_messages = []

        user = User.query.filter_by(email=email).first()
        if user:
            error_messages.append('Email already exists')
        if len(email) < 4:
            error_messages.append('Email must be greater than 4 characters.')
        if len(firstname) < 2:
            error_messages.append('Firstname must be greater than 1 character.')
        if len(lastname) < 2:
            error_messages.append('Lastname must be greater than 1 character.')
        if len(username) < 2:
            error_messages.append('Username must be greater than 1 character.')
        if password != confirm_password:
            error_messages.append("Passwords don't match.")
        if len(password) < 7:
            error_messages.append('Password should be at least 7 characters.')
        if not re.search(r'[A-Z]', password):
            error_messages.append('Password should contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            error_messages.append('Password should contain at least one lowercase letter.')
        if not re.search(r'\d', password):
            error_messages.append('Password should contain at least one digit.')
        if not re.search(r'[!@#$%^&*()_+]', password):
            error_messages.append('Password should contain at least one special character.')

        if not error_messages:
            new_user = User(firstname=firstname, lastname=lastname, username=username, email=email, password=generate_password_hash(password, method='scrypt'))

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for("views.home_page"))
        else:
            for message in error_messages:
                flash(message, category='danger')

    return render_template("sign_up.html", user=current_user)
