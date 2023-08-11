from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from . import db
from bson import ObjectId
import base64
from .watchlist import get_watchlist

db = db.db
admin = Blueprint("admin", __name__)


# Check if user is authorized
@admin.before_request
def is_user_authorized():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    user = session["user"]
    roles = user["roles"] if "roles" in user else []
    if "staff" not in roles:
        flash("You are not authorized to open this page.")
        return redirect(url_for("views.home"))


# Function to check if user has a role
def authorize_roles(authorized_roles=[]):
    user_roles = session["user"]["roles"]
    if any(role in authorized_roles for role in user_roles):
        return True
    else:
        flash("You are not authorized to perform this action.")
    return False


# Dashboard
@admin.route("/")
@admin.route("/dashboard/")
def dashboard():
    services = db.Services.count_documents({})
    watchlist = db.Watchlist.count_documents({})
    users = db.Users.count_documents({})
    subs = db.Subscriptions.count_documents({})
    return render_template(
        "admin/dashboard.html",
        services=services,
        watchlist=watchlist,
        users=users,
        subs=subs,
    )


# List of Services
@admin.route("/services/")
def service_manager():
    filter = {}
    search = request.args.get("search")
    view = request.args.get("view", default="grid")
    if search:
        filter.update(regex_search("name", search))
    services = list(db.Services.find(filter))
    return render_template(
        "admin/services.html", services=services, search=search, view=view
    )


# Watchlist - List of Movies/TV
@admin.route("/watchlist/")
def watchlist_manager():
    page = request.args.get("page", default=1, type=int)
    search = request.args.get("search")
    title_type = request.args.get("type")
    sort_by = request.args.get("sort")
    page_details = {"page": page, "search": search, "type": title_type, "sort": sort_by}
    watchlist = get_watchlist(page, search, title_type, sort_by)
    return render_template(
        "admin/watchlist.html", watchlist=watchlist, page_details=page_details
    )


# List of Users
@admin.route("/users/")
def user_manager():
    filter = {}
    search = request.args.get("search")
    if search:
        or_query = [regex_search("email", search), regex_search("username", search)]
        filter = {"$or": or_query}

    users = db.Users.find(filter)
    return render_template("admin/users.html", users=users)


# Add new Service
@admin.route("/services/new/", methods=["GET", "POST"])
def add_new_service():
    try:
        if request.method == "POST":
            name = request.form.get("name")
            logo = request.files.get("logo")
            logo_wide = request.files.get("logo_wide")

            # Convert images to base64
            logo = convert_img_to_base64(logo)
            logo_wide = convert_img_to_base64(logo_wide)
            db.Services.insert_one(
                {
                    "name": name,
                    "logo": logo,
                    "logo_wide": logo_wide,
                }
            )
            flash("Successfully added a new service!")
            return redirect(url_for("admin.service_manager", search=name))
    except:
        pass
    return render_template("admin/manager/new-service.html")


# View/Edit a Service Details
@admin.route("/services/<service_id>/", methods=["GET", "POST"])
def manage_service(service_id):
    try:
        if request.method == "POST":
            if authorize_roles(["admin"]):
                name = request.form.get("name")
                logo = request.files.get("logo")
                logo_wide = request.files.get("logo_wide")

                data = {"name": name}
                if logo:
                    data["logo"] = convert_img_to_base64(logo)
                if logo_wide:
                    data["logo_wide"] = convert_img_to_base64(logo_wide)
                db.Services.update_one({"_id": ObjectId(service_id)}, {"$set": data})
                flash("Changes saved successfully!")
    except:
        pass

    service = db.Services.find_one({"_id": ObjectId(service_id)})
    if service:
        return render_template("admin/manager/service.html", service=service)
    return redirect(url_for("admin.service_manager"))


# Add new Movie/TV to the Watchlist
@admin.route("/watchlist/new/", methods=["GET", "POST"])
def add_new_watchlist():
    try:
        if request.method == "POST":
            data = request.form.to_dict()
            title = data["title"]
            data["year"] = int(data["year"])
            data["rating"] = float(data["rating"])
            db.Watchlist.update_one({"title": title}, {"$set": data}, upsert=True)
            flash("Successfully added a new title to the watchlist!")
            return redirect(url_for("admin.watchlist_manager", search=title))
    except:
        pass
    return render_template("admin/manager/new-watchlist.html")


# View/Edit a Watchlist Details
@admin.route("/watchlist/<title_id>/", methods=["GET", "POST"])
def manage_watchlist(title_id):
    try:
        if request.method == "POST":
            if authorize_roles(["admin"]):
                data = request.form.to_dict()
                data["year"] = int(data["year"])
                data["rating"] = float(data["rating"])
                db.Watchlist.update_one({"_id": ObjectId(title_id)}, {"$set": data})
                flash("Changes saved successfully!")
    except:
        pass

    watchlist = db.Watchlist.find_one({"_id": ObjectId(title_id)})
    if watchlist:
        return render_template("admin/manager/watchlist.html", watchlist=watchlist)
    return redirect(url_for("admin.watchlist_manager"))


# View/Edit a User Details
@admin.route("/users/<user_id>/", methods=["GET", "POST"])
def manage_user(user_id):
    try:
        if request.method == "POST":
            if authorize_roles(["admin"]):
                form = request.form.to_dict()
                form["roles"] = form["roles"].split(",")
                db.Users.update_one({"_id": ObjectId(user_id)}, {"$set": form})
                flash("Changes saved successfully!")
    except:
        pass

    user = db.Users.find_one({"_id": ObjectId(user_id)})
    if user:
        return render_template("admin/manager/user.html", user=user)
    return redirect(url_for("admin.user_manager"))


# Delete a database record
@admin.route("/delete-item/<collection>/<id>/", methods=["GET", "POST"])
def delete_item(collection, id):
    item = db[collection].find_one({"_id": ObjectId(id)})
    try:
        if request.method == "POST":
            if authorize_roles(["admin"]):
                db[collection].delete_one({"_id": ObjectId(id)})
                flash("Successfully deleted an item.")
                target_url = url_for("admin.dashboard")
                if collection == "Services":
                    target_url = url_for("admin.service_manager")
                elif collection == "Watchlist":
                    target_url = url_for("admin.watchlist_manager")
                elif collection == "Users":
                    target_url = url_for("admin.user_manager")
                return redirect(target_url)
    except:
        pass
    return render_template(
        "admin/manager/delete-item.html", collection=collection, item=item
    )


# Query to find a keyword
def regex_search(field, string):
    query = {field: {"$regex": string, "$options": "i"}}
    return query


# Convert image file to base64
def convert_img_to_base64(image):
    image = image.read()
    image = base64.b64encode(image).decode("utf-8")
    return image
