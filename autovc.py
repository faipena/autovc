#!/usr/bin/env python
# author: faipena
from argparse import ArgumentParser
from flask import Flask, request
from flask_socketio import SocketIO
from filelock import FileLock
import requests
from dataclasses import dataclass
import sys
import os
from tabulate import tabulate
import time

LISTEN_PORT = 18889
LOCAL_API = f"http://127.0.0.1:{LISTEN_PORT}"
VC_API = "http://127.0.0.1:18888"
LOCK_FILE = "autovc_server.lock"

# Classes and functions


def abort(message: str):
    print("ERROR", message)
    sys.exit(1)


@dataclass
class Model:
    index: int | str
    name: str


def get_info(url: str):
    resp = requests.get(f"{url}/info")
    if resp.status_code != 200:
        abort("cannot retrieve information from voice changer server")
    models = [
        Model(index=m["slotIndex"], name=m["name"])
        for m in filter(
            lambda x: x["voiceChangerType"] != None, resp.json()["modelSlots"]
        )
    ]
    return models


# Flask server
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=VC_API)


@app.route("/kill", methods=["PUT"])
def flask_kill():
    os._exit(0)


def add_event_routes(app, routes):
    for route, event in routes:

        def make_handler(event):
            def handler():
                socketio.emit(event)
                return ""

            return handler

        endpoint = f"handle_event{route.replace('/', '_').strip('_')}"
        app.route(route, methods=["PUT"], endpoint=endpoint)(make_handler(event))


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = VC_API
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Commands


def boot():
    with FileLock(LOCK_FILE, blocking=False):
        routes = [
            ("/start", "vc start"),
            ("/stop", "vc stop"),
            ("/monitor", "vc monitor toggle"),
        ]
        add_event_routes(app, routes)
        socketio.run(app=app, host="127.0.0.1", port=LISTEN_PORT)


def kill():
    try:
        requests.put(f"{LOCAL_API}/kill")
    except:
        pass


def event_cmd(event_endpoint: str):
    requests.put(f"{LOCAL_API}/{event_endpoint}")


def list(api_url: str):
    models = get_info(api_url)
    print(tabulate(models, headers=["Index", "Name"]))


def select(api_url: str, model_index: str):
    try:
        model_index = f"{int(model_index):03}"
    except:
        model_index = f"000{model_index}"
    # The following None is used to remove filename from the multi part form
    requests.post(
        f"{api_url}/update_settings",
        files={
            "key": (None, "modelSlotIndex"),
            "val": (None, f"{int(time.time())}{model_index}"),
        },
    )


def main():
    parser = ArgumentParser("autovc", description="Voice Changer automatization")
    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute, defaults to 'boot'"
    )
    _ = subparsers.add_parser("boot", help="Start the autovc server")
    _ = subparsers.add_parser("kill", help="Stop the autovc server")
    _ = subparsers.add_parser("start", help="Start the voice changer")
    _ = subparsers.add_parser("stop", help="Stop the voice changer")
    _ = subparsers.add_parser("monitor", help="Toggle monitor")
    _ = subparsers.add_parser("list", help="List available models")
    select_parser = subparsers.add_parser("select", help="Select a model")
    select_parser.add_argument(
        "INDEX",
        help="Model index to select, use 'list' command to get model names and indexes",
    )
    args = parser.parse_args()
    if args.command in [None, "boot"]:
        boot()
    elif args.command == "kill":
        kill()
    elif args.command == "list":
        list()
    elif args.command == "select":
        select(args.INDEX)
    else:  # start, stop, monitor
        event_cmd(args.command)


if __name__ == "__main__":
    main()
