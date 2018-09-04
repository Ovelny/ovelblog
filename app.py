#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from flask_frozen import Freezer
from flask_flatpages import FlatPages
from flask import Flask, render_template
from typing import Set, Dict, Tuple, List, Optional

app: Flask = Flask(__name__)
app.config.from_pyfile("config.py")
pages: FlatPages = FlatPages(app)
freezer: Freezer = Freezer(app)


@app.route("/")
def home() -> Flask:
    # ::: todo : sort posts by date :::
    return render_template("index.html", pages=pages)


@app.route("/<path:path>/")
def page(path: str) -> Flask:
    page: Flask = pages.get_or_404(path)
    return render_template("page.html", page=page)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run()
