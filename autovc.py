#!/usr/bin/env python
# author: faipena
from argparse import ArgumentParser
from flask import Flask
from flask_socketio import SocketIO
import requests
from dataclasses import dataclass
import sys
from tabulate import tabulate
import time

VC_API = "http://127.0.0.1:18888"
LISTEN_PORT = 18889
LOCAL_API = f"http://127.0.0.1:{LISTEN_PORT}"

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


@app.route("/start", methods=["PUT"])
def flask_start():
    socketio.emit("vc start")
    return {"started": True}, 200


@app.route("/stop", methods=["PUT"])
def flask_stop():
    socketio.emit("vc stop")
    return {"started": False}, 200


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = VC_API
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Commands


def start_server():
    socketio.run(app=app, host="127.0.0.1", port=LISTEN_PORT)


def list(api_url: str):
    models = get_info(api_url)
    print(tabulate(models, headers=["Index", "Name"]))


def start():
    requests.put(f"{LOCAL_API}/start")


def stop(port: int):
    requests.put(f"{LOCAL_API}/stop")


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
    parser = ArgumentParser("autovc", description="Voice Changer Automatization")
    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute, defaults to 'startserver'"
    )
    _ = subparsers.add_parser("start", help="Start the voice changer")
    _ = subparsers.add_parser("stop", help="Stop the voice changer")
    _ = subparsers.add_parser("list", help="List available models")
    _ = subparsers.add_parser("startserver", help="Start the autovc server")
    _ = subparsers.add_parser("stopserver", help="Stop the autovc server")
    select_parser = subparsers.add_parser("select", help="Select a model")
    select_parser.add_argument(
        "INDEX",
        help="Model index to select, use 'list' command to get model names and indexes",
    )
    args = parser.parse_args()
    if args.command in [None, "startserver"]:
        start_server()
    elif args.command == "list":
        list()
    elif args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "select":
        select(args.INDEX)


if __name__ == "__main__":
    main()
