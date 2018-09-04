#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from flask_frozen import Freezer
from flask import Flask, render_template
from typing import Set, Dict, Tuple, List, Optional
from flask_flatpages import FlatPages, pygments_style_defs

app: Flask = Flask(__name__)
app.config.from_pyfile("config.py")
pages: FlatPages = FlatPages(app)
freezer: Freezer = Freezer(app)


@app.route("/")
def home() -> Flask:
    posts = [page for page in pages if "date" in page.meta]
    sorted_posts = sorted(posts, reverse=True, key=lambda page: page.meta["date"])
    return render_template("index.html", pages=sorted_posts)


# :::| todo: custom 404 page |:::
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
# :::| todo: RSS stream |:::


@app.route("/static/pygments.css")
def pygments_css() -> pygments_style_defs:
    return pygments_style_defs("trac"), 200, {"Content-Type": "text/css"}


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
