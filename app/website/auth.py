from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from . import db
import hashlib
from bson import json_util

db = db.db
auth = Blueprint("auth", __name__)


# Check whether user is already logged in
@auth.before_request
def is_user_logged_in():
    if "user" in session and request.endpoint != "auth.logout":
        return redirect(url_for("views.home"))


# Sign up page
@auth.route("/signup/", methods=["GET", "POST"])
def signup():
    form_fields = {"email", "username", "password"}

    if request.method == "POST":
        try:
            form = request.form.to_dict()
            validated = True

            # Check if all fields exist in the form data
            if set(form.keys()) == form_fields:
                # Validate email
                if not validate_email(form["email"]):
                    validated = False
                    flash("Email is either not valid or already exists.")

                # Validate username
                if not validate_username(form["username"]):
                    validated = False
                    flash("Username is not valid.")

                # validate password
                if not validate_password(form["password"]):
                    validated = False
                    flash("Password is not valid.")
            else:
                validated = False
                flash("Please fill all fields.")

            if validated:
                form["password"] = encrypt_message(form["password"])
                db.Users.insert_one(form)
                flash("Successfully created a new account. Please login to continue.")
                return redirect(url_for("auth.login"))
        except:
            flash("Something went wrong. Please try again later.")
            pass

    return render_template("auth/signup.html")


# Log in page
@auth.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = {}
            email = request.form.get("email")
            password = request.form.get("password")

            validated = True
            # Check if email and password exists
            if email and password:
                # Find user
                user = get_user(email)
                if user:
                    password = encrypt_message(password)
                    # Validate password
                    if not user["password"] == password:
                        validated = False
                        flash("Password in incorrect.")
                else:
                    validated = False
                    flash("Email not found.")
            else:
                validated = False
                flash("Please fill all fields.")

            if validated:
                user["_id"] = json_util.dumps(user["_id"]).split('"')[3]
                session["user"] = user
                session.permanent = True
                flash("Successfully logged in.")
                return redirect(url_for("account.dashboard"))

        except:
            flash("Something went wrong. Please try again later.")
            pass

    return render_template("auth/login.html")


# Log out function
@auth.route("/logout")
def logout():
    session.pop("user", None)
    flash("You were successfully logged out.")
    return redirect(request.referrer)


# Function to get user by email
def get_user(email):
    user = None
    try:
        user = db.Users.find_one({"email": email})
    except:
        pass
    return user


# Function to validate email address during signup
def validate_email(email):
    valid = False
    if email:
        if not get_user(email):
            valid = True
    return valid


# Function to validate username during signup
def validate_username(username):
    valid = False
    if username:
        if len(username) >= 5 and username.isalnum():
            valid = True
    return valid


# Function to validate password during signup
def validate_password(password):
    valid = False
    if password:
        if len(password) >= 6:
            valid = True
    return valid


# Function to encrypt a string using MD5 hashing
def encrypt_message(message):
    encrypted_message = hashlib.md5(message.encode()).hexdigest()
    return encrypted_message
