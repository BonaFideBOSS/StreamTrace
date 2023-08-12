from website import flask_app
from flask import render_template

app = flask_app()

if __name__ == "__main__":
    app.run()


@app.context_processor
def get_website_name():
    return dict(website_info=app.config["WEBSITE_INFO"])


# ===== Error Handling =====
@app.errorhandler(Exception)
def page_not_found(e):
    return render_template("404.html")
