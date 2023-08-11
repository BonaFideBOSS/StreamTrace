from flask import session
from . import db
from bson import ObjectId

db = db.db


def get_watchlist(page=1, search=None, title_type=None, sort_by=None):
    watchlist = []
    try:
        page = int(page)
        limit = 100
        skip = (page - 1) * limit

        filter = {}
        sort = [("year", -1)]
        if search:
            query = [{"title": {"$regex": i, "$options": "i"}} for i in search.split()]
            filter = {"$and": query}
        if title_type in ["Movie", "TV"]:
            filter["type"] = title_type
        if sort_by == "oldest":
            sort = [("year", 1)]
        elif sort_by == "rating_high":
            sort = [("rating", -1)]
        elif sort_by == "rating_low":
            sort = [("rating", 1)]
        elif sort_by == "title_asc":
            sort = [("title", 1)]
        elif sort_by == "title_desc":
            sort = [("title", -1)]

        watchlist = list(db.Watchlist.find(filter).sort(sort).skip(skip).limit(limit))
    except:
        pass
    return watchlist


def get_user_watchlist(page=1, search=None, title_type=None, sort_by=None, limit=100):
    watchlist = []
    try:
        page = int(page)
        skip = (page - 1) * limit

        filter = {}
        if search:
            query = [{"title": {"$regex": i, "$options": "i"}} for i in search.split()]
            filter = {"$and": query}
        if title_type in ["Movie", "TV"]:
            filter["type"] = title_type

        sort = {"date_added": -1}
        if sort_by == "latest":
            sort = {"year": -1}
        if sort_by == "oldest":
            sort = {"year": 1}
        elif sort_by == "rating_high":
            sort = {"rating": -1}
        elif sort_by == "rating_low":
            sort = {"rating": 1}
        elif sort_by == "title_asc":
            sort = {"title": 1}
        elif sort_by == "title_desc":
            sort = {"title": -1}

        user_id = session["user"]["_id"]
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {
                "$lookup": {
                    "from": "Watchlist",
                    "localField": "watchlist_id",
                    "foreignField": "_id",
                    "as": "watchlist",
                }
            },
            {"$unwind": "$watchlist"},
            {
                "$project": {
                    "_id": 1,
                    "user_id": 1,
                    "watchlist_id": 1,
                    "date_added": 1,
                    "type": "$watchlist.type",
                    "title": "$watchlist.title",
                    "year": "$watchlist.year",
                    "rating": "$watchlist.rating",
                    "poster": "$watchlist.poster",
                }
            },
            {"$match": filter},
            {"$sort": sort},
            {"$skip": skip},
            {"$limit": limit},
        ]
        watchlist = list(db.UserWatchlist.aggregate(pipeline))
    except Exception as e:
        print(e)
        pass
    return watchlist
