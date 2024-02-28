from functools import wraps

from flask import Blueprint, render_template, url_for, redirect, session

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo

from password_validator import PasswordValidator

import games.utilities.utilities as utilities
import games.authentication.services as services
import games.adapters.repository as repo

# Configure Blueprint
authentication_blueprint = Blueprint(
    'authentication_bp', __name__, url_prefix='/authentication')


@authentication_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    featured_genres = utilities.get_featured_genres()

    username_not_unique = None

    if form.validate_on_submit():
        # Successful POST -- the username & password have passed validation checking
        # Use the service layer to attempt to add the new user
        try:
            services.add_user(form.username.data, form.password.data, repo.repo_instance)

            # Success, redirect the user to login page
            return redirect(url_for("authentication_bp.login"))
        except services.NameNotUniqueException:
            username_not_unique = "Username is already taken. Please try again."

    # For a GET or failed POST request, return the Registration web page
    return render_template(
        'authentication/credentials.html',
        title="Sign Up | CS235 Game Library",
        form_title="Sign Up",
        handler_url=url_for("authentication_bp.register"),
        username_error_message=username_not_unique,
        password_error_message=None,
        form=form,
        featured_genres=featured_genres,
    )


@authentication_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username_not_recognised = None
    password_does_not_match_username = None
    featured_genres = utilities.get_featured_genres()

    if form.validate_on_submit():
        # Successful POST, so the username and password have passed validation checks
        # Use service layer to look up user
        try:
            user = services.get_user(form.username.data, repo.repo_instance)

            # Authenticate user
            services.authenticate_user(user['username'], form.password.data, repo.repo_instance)

            # Prior to clearing the session, get the current theme so this can persist after the user logs in
            current_theme = session.get('theme')

            # Initialise session and redirect user to home page
            session.clear()

            # Set the theme as whatever it was prior to login for better UX
            session['theme'] = current_theme
            session['username'] = user['username']

            return redirect(url_for("home_bp.home"))

        except services.UnknownUserException:
            # Username does not exist, so set corresponding error message
            username_not_recognised = "Username not recognised. Please try again or sign up."

        except services.AuthenticationException:
            # Authentication failed, so set corresponding error message
            password_does_not_match_username = "Incorrect password. Please try again."

    # For a GET or a failed POST request, return the Login web page
    return render_template(
        'authentication/credentials.html',
        title="Log In | CS235 Game Library",
        form_title="Log In",
        form=form,
        handler_url=url_for("authentication_bp.login"),
        featured_genres=featured_genres,
        username_error_message=username_not_recognised,
        password_error_message=password_does_not_match_username,
    )

@authentication_blueprint.route('/logout', methods=['GET'])
def logout():
    # Prior to clearing the session, get the current theme so this can persist after the user logs in
    current_theme = session.get('theme')

    session.clear()

    # Set the theme as whatever it was prior to login for better UX
    session['theme'] = current_theme

    return redirect(url_for("home_bp.home"))

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "username" not in session:
            return redirect(url_for("authentication_bp.login"))

        try:
            services.get_user(session["username"], repo.repo_instance)
        # If the user doesn't exist while the session persists, this should raise an exception & redirect to sign up
        except services.UnknownUserException:
            session.clear()
            return redirect(url_for('authentication_bp.register'))

        return view(**kwargs)

    return wrapped_view

class PasswordValid:
    def __init__(self, message=None):
        if not message:
            message = u"Password must be at least 8 characters long and contain an uppercase character, lowercase " \
                      u"character, and a digit from 0-9."
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema \
            .min(8) \
            .has().uppercase() \
            .has().lowercase() \
            .has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        DataRequired(message="Username is required"),
        Length(min=3, max=256, message="Username must be between 3 and 256 characters long.")
    ])
    password = PasswordField("Password", [
        DataRequired(message="Password is required"),
        # Only validate the actual password, otherwise we're just repeating 2 sets of error messages.
        # The confirmation should have the same errors anyway, otherwise the passwords don't match error will appear.
        PasswordValid(),
        EqualTo('password_confirmation', message='Passwords must match')
    ])
    password_confirmation = PasswordField("Confirm password", [
        DataRequired(message="Password confirmation required"),
    ])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField('Username', [
        DataRequired()
    ])
    password = PasswordField('Password', [
        DataRequired()
    ])
    submit = SubmitField("Login")
