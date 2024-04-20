from flask import Blueprint, request
from bs4 import BeautifulSoup
import requests
import json


scraper = Blueprint("scraper", __name__)


def scrape_url(url):
    data = ""
    message = ""
    try:
        connection = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"}
        )
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
            page_data = page.find(id="__NEXT_DATA__")
            page_data = json.loads(page_data.get_text())
            title_data = page_data["props"]["pageProps"]["aboveTheFoldData"]
            title = page.select_one("h1").get_text()
            year = title_data["releaseYear"]["year"]
            rating = title_data["ratingsSummary"]["aggregateRating"]
            poster = page.select_one(".ipc-media img")["src"]

            data["type"] = title_type
            data["title"] = title
            data["year"] = year
            data["rating"] = rating
            data["poster"] = poster
    except Exception as e:
        print(e)
        pass
    return data
