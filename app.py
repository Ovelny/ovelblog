#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
from flask_frozen import Freezer
from typing import Set, Dict, Tuple, List, Optional
from flask_flatpages import FlatPages, pygments_style_defs
from flask import Flask, render_template, make_response, send_from_directory

app: Flask = Flask(__name__)
app.config.from_pyfile("config.py")
pages: FlatPages = FlatPages(app)
freezer: Freezer = Freezer(app)


def sorted_by_date(pages: FlatPages) -> List:
    posts: List = [page for page in pages if "date" in page.meta]
    sorted_posts: List = sorted(posts, reverse=True, key=lambda page: page.meta["date"])
    return sorted_posts

"""@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')"""


# :::| homepage with sorted articles |:::
@app.route("/")
def home() -> Flask:
    sorted_posts: List = sorted_by_date(pages)
    return render_template("index.html", pages=sorted_posts)


# :::| custom 404 page |:::
@app.errorhandler(404)
def page_not_found(e: str) -> Flask:
    return render_template("404.html"), 404


# :::| RSS feed |:::
@app.route("/atom.xml")
def feed() -> Flask:
    sorted_posts: List = sorted_by_date(pages)
    template: Flask = render_template("atom.xml", pages=sorted_posts)
    response: Flask = make_response(template)
    response.headers["Content-Type"] = "text/xml"
    return response


# :::| pygments css to render code highlighting |:::
@app.route("/static/pygments.css")
def pygments_css() -> pygments_style_defs:
    return pygments_style_defs("trac"), 200, {"Content-Type": "text/css"}


# :::| articles and other pages rendering |:::
@app.route("/<path:path>/")
@app.route("/blog/<path:path>/")
def page(path: str) -> Flask:
    page: Flask = pages.get_or_404(path)
    return render_template("page.html", page=page)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run()
