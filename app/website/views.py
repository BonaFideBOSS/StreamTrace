from flask import (
    Blueprint,
    render_template,
    session,
    request,
    flash,
    redirect,
    url_for,
)
from . import db
from .watchlist import get_watchlist

db = db.db
views = Blueprint("views", __name__)


@views.route("/")
def start():
    if "user" in session:
        return redirect(url_for("account.dashboard"))
    else:
        return redirect(url_for("views.home"))


@views.route("/home/")
def home():
    services_count = db.Services.count_documents({})
    services = db.Services.find({}).limit(10)
    return render_template(
        "home.html", services_count=services_count, services=services
    )


@views.route("/streaming-services/")
def services():
    filter = {}
    search = request.args.get("search")
    if search:
        query = [{"name": {"$regex": word, "$options": "i"}} for word in search.split()]
        filter = {"$and": query}
    services = list(db.Services.find(filter))
    return render_template("services.html", services=services, search=search)


@views.route("/browse/")
def browse():
    page = request.args.get("page", default=1, type=int)
    search = request.args.get("search")
    title_type = request.args.get("type")
    sort_by = request.args.get("sort")
    page_details = {"page": page, "search": search, "type": title_type, "sort": sort_by}
    watchlist = get_watchlist(page, search, title_type, sort_by)
    return render_template(
        "browse.html", watchlist=watchlist, page_details=page_details
    )


@views.route("/about/")
def about():
    services = db.Services.count_documents({})
    subs = db.Subscriptions.count_documents({})
    users = db.Users.count_documents({})
    return render_template("about.html", services=services, subs=subs, users=users)


@views.route("/contact/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        form = request.form.to_dict()
        flash("Thank you for your message! We will reply you back soon.")
    return render_template("contact.html")


@views.route("/terms/")
def terms():
    return render_template("legal/terms.html")


@views.route("/privacy/")
def privacy():
    return render_template("legal/privacy.html")


@views.route("/theme-changer")
def theme_changer():
    theme = "dark"
    if "theme" in session:
        theme = session["theme"]
    theme = "light" if theme == "dark" else "dark"
    session["theme"] = theme
    return theme


@views.route("/subscribe")
def subscribe():
    flash("Thank you for subscribing!")
    return redirect(request.referrer)

@views.route("/ping/")
def ping():
    return "live"