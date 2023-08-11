from flask import Blueprint, request
from bs4 import BeautifulSoup
import requests


scraper = Blueprint("scraper", __name__)


def scrape_url(url):
    data = ""
    message = ""
    try:
        connection = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = BeautifulSoup(connection.text, "lxml")
        connection.close()
    except Exception as e:
        message = e
    return {"data": data, "message": message}


@scraper.route("/scrape-imdb-title-page")
def scrape_imdb_title_page():
    data = {
        "type": "",
        "title": "",
        "year": "",
        "rating": "",
        "poster": "",
    }
    try:
        url = request.args.get("url")
        title_type = request.args.get("type")
        scrape = scrape_url(url)
        page = scrape["data"]
        if page:
            title = page.select_one("h1").get_text()
            year = page.select_one(".sc-e226b0e3-3 li a").get_text()
            year = year.split("–")[0]
            rating = page.select_one("span.sc-bde20123-1.iZlgcd").get_text()
            poster = page.select_one(".ipc-media img")["src"]

            data["type"] = title_type
            data["title"] = title
            data["year"] = int(year)
            data["rating"] = float(rating)
            data["poster"] = poster
    except Exception as e:
        print(e)
        pass
    return data
