#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from typing import Set, Dict, Tuple, List, Optional


def parent_dir(path: str) -> str:
    return os.path.abspath(os.path.join(path, os.pardir))


# ::: paths & locations :::
HERE: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT: str = parent_dir(HERE)

# ::: freezer config :::
REPO_NAME: str = "ovelblog"
FREEZER_DESTINATION: str = HERE
FREEZER_REMOVE_EXTRA_FILES: bool = False
FREEZER_BASE_URL: str = "http://localhost/{0}".format(REPO_NAME)

# ::: flatpages config :::
DEBUG: bool = True
FLATPAGES_EXTENSION: str = ".md"
FLATPAGES_AUTO_RELOAD: bool = True
FLATPAGES_ROOT: str = os.path.join(HERE, "pages")
FLATPAGES_MARKDOWN_EXTENSIONS: List[str] = ["codehilite"]