#!/usr/bin/env python
# author: faipena
from argparse import ArgumentParser
import requests
from dataclasses import dataclass
import sys
from tabulate import tabulate
from flask import Flask, Response
import time

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
        Model(index=m["slotIndex"], name=m["name"]) for m in
          filter(lambda x: x["voiceChangerType"] != None, resp.json()["modelSlots"])
    ]
    return models

# Flask server

voice_changer_started = False
app = Flask(__name__)

def start_server(started: bool, port: int):
    global voice_changer_started
    voice_changer_started = started
    app.run(host="127.0.0.1", port=port)

@app.route("/")
def flask_index():
    global voice_changer_started
    return {"started": voice_changer_started}, 200

@app.route("/start")
def flask_start():
    global voice_changer_started
    voice_changer_started = True
    return {"started": voice_changer_started}, 200

@app.route("/stop")
def flask_stop():
    global voice_changer_started
    voice_changer_started = False
    return {"started": voice_changer_started}, 200

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:18888"  # Allow all origins
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Commands

def list(api_url: str):
    models = get_info(api_url)
    print(tabulate(models, headers=["Index", "Name"]))

def start(port: int):
    try:
        requests.get(f"http://127.0.0.1:{port}/start")
    except requests.exceptions.ConnectionError:
        start_server(True, port)


def stop(port: int):
    try:
        requests.get(f"http://127.0.0.1:{port}/stop")
    except requests.exceptions.ConnectionError:
        start_server(False, port)

def select(api_url: str, model_index: str):
    try:
        model_index = f"{int(model_index):03}"
    except:
        model_index = f"000{model_index}"
    # The following None is used to remove filename from the multi part form
    requests.post(f"{api_url}/update_settings", files={
        "key": (None,"modelSlotIndex"),
        "val": (None,f"{int(time.time())}{model_index}")
        })

def main():
    parser = ArgumentParser(__name__, description="Voice Changer Automatization")
    parser.add_argument("--api-url", default="http://127.0.0.1:18888", help="URL for the rest API interface of voice changer")
    parser.add_argument("--port", default=18889, type=int, help="Port where autovc should listen when run in server mode")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute", required=True)
    _ = subparsers.add_parser("start", help="Start the voice changer")
    _ = subparsers.add_parser("stop", help="Stop the voice changer")
    _ = subparsers.add_parser("list", help="List available models")
    select_parser = subparsers.add_parser("select", help="Select a model")
    select_parser.add_argument("INDEX", help="Model index to select, use 'list' command to get model names and indexes")
    args = parser.parse_args()
    if args.port > 2**16-1 or args.port < 0:
        abort(f"Invalid port value, must be between 0 and {2**16-1}")
    if args.command == "list":
        list(args.api_url)
    elif args.command == "start":
        start(args.port)
    elif args.command == "stop":
        stop(args.port)
    elif args.command == "select":
        select(args.api_url, args.INDEX)

if __name__ == "__main__":
    main()
