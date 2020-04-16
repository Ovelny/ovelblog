#!/usr/bin/env python3
import os
import re
import config
import urllib.request

"""
This module is a custom extension of the Frozen-Flask build
process found in app.py. It provides the following steps for
each build:

- Retrieve all dropbox URLs found in each blog posts
- Create a directory for each post in /static/images to store related pictures
- Download all pictures from dropbox paper and store them in said directories
- Replace all dropbox links in corresponding posts with local links

It essentially allows me to dump anything I write on dropbox paper
to my blog, seamlessly.
"""

dropbox_base_url = "https://paper-attachments.dropbox.com/"
img_base_path = "static/images"


def img_dir(dirname):
    """
    Return the full path of the image directory
    for the related post
    """
    return os.path.join(img_base_path, dirname)


def dirname(filename):
    """
    Return the directory name for each post: 
    the post's title without its .md extension
    """
    return os.path.splitext(filename)[0]


def set_img_dir_by_post(filename):
    if not os.path.isdir(img_dir(dirname(filename))):
        os.mkdir(img_dir(dirname(filename)))


def download_imgs(filename, imgs):
    for img in imgs:
        img_name = img.replace(dropbox_base_url, "")
        urllib.request.urlretrieve(
            img, os.path.join(img_dir(dirname(filename)), img_name)
        )


def get_img_links_in_post(filepath):
    img_links = []
    with open(filepath, "r") as f:
        for line in f:
            if dropbox_base_url in line:
                url = re.search("(?P<url>https?://[^\s]+)", line).group("url")
                url = url.replace(")", "")
                img_links.append(url)
    return img_links


def replace_img_links_in_post(filepath, filename):
    new_img_path = os.path.join(config.FREEZER_BASE_URL, img_dir(dirname(filename)), "")
    with open(filepath, "r") as f:
        filedata = f.read()
    filedata = filedata.replace(dropbox_base_url, new_img_path)
    with open(filepath, "w") as f:
        f.write(filedata)


def replace():
    for filename in os.listdir("posts"):
        if filename.endswith(".md"):
            filepath = f"posts/{filename}"
            set_img_dir_by_post(filename)
            imgs = get_img_links_in_post(filepath)
            download_imgs(filename, imgs)
            replace_img_links_in_post(filepath, filename)


if __name__ == "__main__":
    replace()
