from flask import (
    Blueprint,
    render_template,
    session,
    request,
    flash,
    redirect,
    url_for,
    abort,
)
from . import db
from .auth import validate_username, validate_email, validate_password, encrypt_message
from bson import ObjectId, json_util
from datetime import datetime
from .watchlist import get_user_watchlist

db = db.db
account = Blueprint("account", __name__)


# Check if user is logged in
@account.before_request
def is_user_logged_in():
    if "user" not in session:
        return redirect(url_for("auth.login"))


# Dashboard Page
@account.route("/dashboard/")
def dashboard():
    user_id = ObjectId(session["user"]["_id"])
    sub_count = db.Subscriptions.count_documents({"user": user_id})
    wlist_count = db.UserWatchlist.count_documents({"user_id": user_id})
    return render_template(
        "account/dashboard.html", sub_count=sub_count, wlist_count=wlist_count
    )


# Watchlist Page
@account.route("/watchlist/")
def watchlist():
    page = request.args.get("page", default=1, type=int)
    search = request.args.get("search")
    title_type = request.args.get("type")
    sort_by = request.args.get("sort")
    page_details = {"page": page, "search": search, "type": title_type, "sort": sort_by}
    watchlist = get_user_watchlist(page, search, title_type, sort_by)
    return render_template(
        "account/watchlist.html", watchlist=watchlist, page_details=page_details
    )


# Account Settings Page
@account.route("/account/")
def home():
    return render_template("account/account.html")


# Function to get User Subscriptions
@account.route("/user-subs")
def user_subs():
    subs = []
    try:
        user_id = session["user"]["_id"]
        pipeline = [
            {"$match": {"user": ObjectId(user_id)}},
            {
                "$lookup": {
                    "from": "Services",
                    "localField": "service",
                    "foreignField": "_id",
                    "as": "service",
                }
            },
        ]
        subs = list(db.Subscriptions.aggregate(pipeline))
        subs = json_util.dumps(subs)
    except:
        pass
    return subs


# Dashboard Chart Function - Sum of Expenses by Services
@account.route("/sum-of-amount-by-services")
def sum_of_amount_by_services():
    user_id = ObjectId(session["user"]["_id"])
    user_filter = [{"$match": {"user": user_id}}]
    group = {"_id": "$service", "count": {"$sum": 1}}
    group["count"]["$sum"] = "$amount"
    pipeline = user_filter + [
        {"$group": group},
        {
            "$lookup": {
                "from": "Services",
                "localField": "_id",
                "foreignField": "_id",
                "as": "service_detail",
            }
        },
        {
            "$project": {
                "service": {"$arrayElemAt": ["$service_detail.name", 0]},
                "sum": "$count",
                "_id": 0,
            }
        },
        {"$sort": {"sum": -1}},
    ]
    result = list(db.Subscriptions.aggregate(pipeline))
    return json_util.dumps(result)


# Dashboard Chart Function - Monthly Breakdown
@account.route("/monthly-breakdown")
def monthly_breakdown():
    user_id = ObjectId(session["user"]["_id"])
    user_filter = [{"$match": {"user": user_id}}]
    group = {"_id": {"month": {"$month": "$expiry"}}, "count": {"$sum": "$amount"}}
    pipeline = user_filter + [
        {"$group": group},
        {
            "$project": {
                "month": "$_id.month",
                "sum": "$count",
                "_id": 0,
            }
        },
        {"$sort": {"month": 1}},
    ]
    result = list(db.Subscriptions.aggregate(pipeline))
    return json_util.dumps(result)


# Dashboard Function - Get user watchlist
@account.route("/get-db-watchlist")
def get_db_watchlist():
    watchlist = get_user_watchlist(limit=9)
    return json_util.dumps(watchlist)


# Function to add new Subscription
@account.route("/subscriptions/new/<service_id>", methods=["GET", "POST"])
def new_sub(service_id):
    service = db.Services.find_one({"_id": ObjectId(service_id)})
    if not service:
        return redirect(url_for("views.services"))

    try:
        form_fields = {"name", "amount", "expiry"}
        if request.method == "POST":
            form = request.form.to_dict()
            valid = True

            if set(form.keys()) == form_fields:
                # Check if subscription already exists
                if len(check_duplicate_sub(service_id, form["name"])) != 0:
                    valid = False
                    flash("A subscription with the same account already exists.")

                form["amount"] = float(form["amount"])
                form["expiry"] = datetime.strptime(form["expiry"], "%Y-%m-%d")

                if valid:
                    form["service"] = ObjectId(service_id)
                    form["user"] = ObjectId(session["user"]["_id"])
                    db.Subscriptions.insert_one(form)
                    flash("Subscription added successfully!")
                    return redirect(url_for("account.dashboard"))
            else:
                flash("Please fill all field.")
    except:
        flash("Something went wrong. Please try again later.")
    return render_template("account/new-sub.html", service=service)


# Function to edit a Subscription
@account.route("/subscriptions/manage/<sub_id>", methods=["GET", "POST"])
def edit_sub(sub_id):
    pipeline = [
        {"$match": {"_id": ObjectId(sub_id)}},
        {
            "$lookup": {
                "from": "Services",
                "localField": "service",
                "foreignField": "_id",
                "as": "service",
            }
        },
    ]
    sub = list(db.Subscriptions.aggregate(pipeline))
    if len(sub) == 0:
        return redirect(url_for("account.dashboard"))
    else:
        sub = sub[0]

    try:
        form_fields = {"amount", "expiry"}
        if request.method == "POST":
            form = request.form.to_dict()
            valid = True

            if set(form.keys()) == form_fields:
                form["amount"] = float(form["amount"])
                form["expiry"] = datetime.strptime(form["expiry"], "%Y-%m-%d")

                if valid:
                    query = {"_id": ObjectId(sub_id)}
                    db.Subscriptions.update_one(query, {"$set": form})
                    flash("Subscription updated successfully!")
                    return redirect(url_for("account.dashboard"))
            else:
                flash("Please fill all field.")
    except:
        flash("Something went wrong. Please try again later.")

    return render_template("account/edit-sub.html", sub=sub)


# Function to delete a Subscription
@account.route("/delete-sub/<sub_id>/")
def delete_sub(sub_id):
    response = ""
    success = False
    try:
        sub_id = ObjectId(sub_id)
        user_id = ObjectId(session["user"]["_id"])
        sub = db.Subscriptions.find_one({"_id": sub_id, "user": user_id})
        db.Subscriptions.delete_one(sub)
        response = "Subscription deleted successfully!"
        flash(response)
        success = True
    except:
        response = "Failed to delete subscription."
    return {"response": response, "success": success}


# Function to check for duplicate Subscriptions
def check_duplicate_sub(service_id, sub_name):
    query = {"service": ObjectId(service_id), "name": sub_name}
    query["user"] = ObjectId(session["user"]["_id"])
    result = db.Subscriptions.find(query).collation({"locale": "en", "strength": 1})
    return list(result)


# Function to add movie/tv to watchlist
@account.route("/add-to-watchlist")
def add_to_watchlist():
    response = "Failed to add to watchlist."
    try:
        watchlist_id = request.args.get("watchlist_id")
        if not watchlist_id:
            return response
        watchlist_id = ObjectId(watchlist_id)
        watchlist = db.Watchlist.find_one({"_id": watchlist_id})
        if not watchlist:
            return response
        user_id = ObjectId(session["user"]["_id"])
        query = {"user_id": user_id, "watchlist_id": watchlist_id}
        data = {"date_added": datetime.now()}
        db.UserWatchlist.update_one(query, {"$set": data}, upsert=True)
        response = "Successfully added to watchlist!"
    except:
        response = f"{response} Please try again later."
    return response


# Function to remove movie/tv from watchlist
@account.route("/del-from-watchlist")
def del_from_watchlist():
    response = "Failed to remove from watchlist."
    success = False
    try:
        watchlist_id = request.args.get("watchlist_id")
        if not watchlist_id:
            return response
        query = {"_id": ObjectId(watchlist_id)}
        db.UserWatchlist.delete_one(query)
        response = "Successfully removed from watchlist."
        success = True
    except:
        response = f"{response} Plese try again later."
    return {"response": response, "success": success}


# Function to update personal details
@account.route("/update-personal")
def update_personal_details():
    response = ""
    form_fields = {"username", "first_name", "last_name", "phone", "age"}
    try:
        data = request.args.to_dict()
        valid = True

        # Check if all fields exist in the form data
        if set(data.keys()) == form_fields:
            if not validate_username(data["username"]):
                valid = False
                response = "Username is not valid."
        else:
            valid = False
            response = "Failed to update."

        if data["phone"]:
            data["phone"] = int(data["phone"])
        if data["age"]:
            data["age"] = int(data["age"])

        if valid:
            user_id = session["user"]["_id"]
            db.Users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
            session["user"].update(data)
            response = "Personal details updated successfully!"
    except:
        response = "Failed to update."
    return response


# Function to update email
@account.route("/update-email")
def update_email():
    response = ""
    try:
        email = request.args.get("email")
        if email == session["user"]["email"]:
            return "No changes were made."

        if validate_email(email):
            user_id = session["user"]["_id"]
            db.Users.update_one({"_id": ObjectId(user_id)}, {"$set": {"email": email}})
            session["user"]["email"] = email
            response = "Email updated successfully!"
        else:
            response = "Email already exists."
    except:
        response = "Failed to update."
    return response


# Function to update password
@account.route("/update-password")
def update_password():
    response = ""
    try:
        old_password = request.args.get("old")
        new_password = request.args.get("new")
        old_password = encrypt_message(old_password)

        valid = True
        if old_password != session["user"]["password"]:
            valid = False
            return "Old password is incorrect."

        if not validate_password(new_password):
            valid = False
            return "Password is not valid."

        new_password = encrypt_message(new_password)
        if old_password == new_password:
            return "No changes were made."

        if valid:
            user_id = session["user"]["_id"]
            data = {"password": new_password}
            db.Users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
            session["user"]["password"] = new_password
            response = "Password updated successfully!"
    except:
        response = "Failed to update."
    return response


# Function to delete user account
@account.route("/delete-account", methods=["POST"])
def delete_account():
    try:
        user_id = session["user"]["_id"]
        user_id = ObjectId(user_id)
        db.Subscriptions.delete_many({"user": user_id})
        db.UserWatchlist.delete_many({"user_id": user_id})
        db.Users.delete_one({"_id": user_id})
        session.pop("user", None)
        flash("Successfully deleted your account. We'll miss you!")
        return redirect(url_for("auth.login"))
    except:
        flash("Failed to delete your account.")
    return redirect({"account.home"})
