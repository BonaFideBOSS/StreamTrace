from flask import Flask
from flask_pymongo import PyMongo
import os

db = PyMongo()


def flask_app():
    app = Flask(__name__, template_folder="views", static_folder="assets")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

    app.config["WEBSITE_INFO"] = {
        "name": "StreamTrace",
        "logo": '<i class="bi bi-cast"></i>',
    }

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .account import account
    from .admin import admin
    from .scraper import scraper

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(account, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(scraper, url_prefix="/scraper")

    return app
