#!/usr/bin/env python
# author: faipena
from argparse import ArgumentParser
from flask import Flask, request
from flask_socketio import SocketIO
from filelock import FileLock
import requests
import os

LISTEN_PORT = 18889
LOCAL_API = f"http://127.0.0.1:{LISTEN_PORT}"
VC_API = "http://127.0.0.1:18888"
LOCK_FILE = "autovc_server.lock"


# Flask server
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=VC_API)


@app.route("/kill", methods=["PUT"])
def flask_kill():
    os._exit(0)


@app.route("/start", methods=["PUT"])
def flask_start():
    socketio.emit("vc start")
    return ""


@app.route("/stop", methods=["PUT"])
def flask_stop():
    socketio.emit("vc stop")
    return ""


@app.route("/monitor", methods=["PUT"])
def flask_monitor():
    socketio.emit("vc monitor toggle")
    return ""


@app.route("/select", methods=["PUT"])
def flask_select():
    data = request.json
    socketio.emit("vc model select", data["model_index"])
    return ""


@app.route("/tune/slide", methods=["PUT"])
def flask_tune_slide():
    data = request.json
    socketio.emit("vc tune slide", data["direction"])
    return ""


@app.route("/tune", methods=["POST"])
def flask_tune():
    data = request.json
    socketio.emit("vc tune set", data["level"])
    return ""


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = VC_API
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Commands


def boot():
    with FileLock(LOCK_FILE, blocking=False):
        socketio.run(app=app, host="127.0.0.1", port=LISTEN_PORT)


def kill():
    try:
        requests.put(f"{LOCAL_API}/kill")
    except:
        pass


def event_cmd(event_endpoint: str):
    requests.put(f"{LOCAL_API}/{event_endpoint}")


def select(model_index: int):
    requests.put(f"{LOCAL_API}/select", json={"model_index": model_index})


def tune(tune_value: str):
    if tune_value in ["up", "down"]:
        requests.put(f"{LOCAL_API}/tune/slide", json={"direction": tune_value})
    else:
        requests.post(f"{LOCAL_API}/tune", json={"level": tune_value})


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
    select_parser = subparsers.add_parser("select", help="Select a model")
    select_parser.add_argument(
        "INDEX", help="Model index to select (alphabetic sort)", type=int
    )
    tune_parser = subparsers.add_parser("tune", help="Interact with the tune slider")
    tune_parser.add_argument(
        "TUNE",
        help="The direction to slide the tune (up/down) or the tune value (an integer between -50 and 50).",
        choices=["up", "down", *(f"{i}" for i in range(-50, 51))],
        metavar="DIRECTION_OR_VALUE",
    )
    args = parser.parse_args()
    if args.command in [None, "boot"]:
        boot()
    elif args.command == "kill":
        kill()
    elif args.command == "select":
        select(args.INDEX)
    elif args.command == "tune":
        tune(args.TUNE)
    else:  # start, stop, monitor
        event_cmd(args.command)


if __name__ == "__main__":
    main()
