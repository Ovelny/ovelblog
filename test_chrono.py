#!/usr/bin/env python
import os
import sys
import csv
import pendulum

chronolog = os.path.expanduser("~/code/ovelny.github.io/chronolog.txt")


def logs_collection(chronolog):
    logs_collection = []
    with open(chronolog) as chrono:
        for log in chrono:
            log = log.rstrip("\n").split("\t")
            log_date = log[0]
            log_content = log[1]
            logged_since = pendulum.parse(log_date).diff_for_humans()

            logs_collection.append(
                {
                    "log_date": log_date,
                    "logged_since": logged_since,
                    "log_content": log_content,
                }
            )

    print(logs_collection)


logs_collection(chronolog)
