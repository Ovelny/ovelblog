#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import csv
from flask_frozen import Freezer
from flask_flatpages import FlatPages, pygments_style_defs
from flask import Flask, render_template, make_response, send_from_directory

app = Flask(__name__)
app.config.from_pyfile("config.py")
pages = FlatPages(app)
freezer = Freezer(app)


def sorted_by_date(pages):
    posts = [page for page in pages if "date" in page.meta]
    sorted_posts = sorted(posts, reverse=True, key=lambda page: page.meta["date"])
    return sorted_posts


# Parsing logs for chronolog:
# open chronolog.txt, strip newlines for each line
# separate timestamp + actual log by splitting each line with tab delimitation
# make a dict for each log, and append it to logs_collection
def logs_collection(chronolog_file):
    logs_collection = []

    with open(chronolog_file) as chrono:
        for log in chrono:
            log = log.rstrip("\n").split("\t")
            log_date = log[0]
            log_content = log[1]
            logs_collection.append({"log_date": log_date, "log_content": log_content})

    logs_collection.reverse()
    return logs_collection


# :::| homepage with sorted articles |:::
@app.route("/")
def home():
    sorted_posts = sorted_by_date(pages)
    return render_template("index.html", pages=sorted_posts)


# :::| custom 404 page |:::
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# :::| RSS feed |:::
@app.route("/atom.xml")
def feed():
    sorted_posts = sorted_by_date(pages)
    template = render_template("atom.xml", pages=sorted_posts)
    response = make_response(template)
    response.headers["Content-Type"] = "text/xml"
    return response


# :::| chronolog, a personal microblogging page |:::
@app.route("/chronolog.html")
def chronolog():
    chronolog_file = os.path.expanduser("~/code/ovelny.github.io/chronolog.txt")
    logs = logs_collection(chronolog_file)
    return render_template("chronolog.html", logs=logs)


# :::| pygments css to render code highlighting |:::
@app.route("/static/pygments.css")
def pygments_css():
    return pygments_style_defs("monokai"), 200, {"Content-Type": "text/css"}


# :::| articles and other pages rendering |:::
@app.route("/<path:path>/")
@app.route("/blog/<path:path>/")
def page(path):
    page = pages.get_or_404(path)
    return render_template("page.html", page=page)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run()
