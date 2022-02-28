import random
from flask import (
    Flask,
    request,
    Response,
    jsonify,
    send_from_directory,
)
import json
from flask_cors import CORS
from webui import WebUI
import serial
import sys
import os
import time

import struct
import datetime
from datetime import date, timedelta
from constants import SEND_CONFIG

ser = serial.Serial()

global start
try:
    f = open("config.json")
    config = json.load(f)
    COM_PORT = config["COM_PORT"]
except:
    sys.exit(
        "Configurtion file not found. Please check the config.json file. Exiting..."
    )


app = Flask(__name__, static_url_path="", static_folder="build")
ui = WebUI(app, debug=True)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    """Return index.html for all non-api routes"""
    if path != "" and os.path.exists(f"{app.static_folder}/{path}"):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


def compute_float(bytes_rec):
    data = []
    bytes_rec = list(bytes_rec)
    del bytes_rec[-1]
    del bytes_rec[-1]  ## deletes last 2 bytes (Checksum)
    del bytes_rec[:3]  ##
    for i in range(0, len(bytes_rec), 4):
        list1 = [bytes_rec[i + 1], bytes_rec[i], bytes_rec[i + 3], bytes_rec[i + 2]]
        final_val = list(struct.unpack("<f", bytearray(list1)))
        data.append(round(final_val[0], 2))

    return data


def checksum_func(arr):
    checksum = 0xFFFF
    for num in range(0, len(arr) - 2):
        lsb = arr[num]
        checksum = checksum ^ lsb
        for count in range(1, 9):
            lastbit = checksum & 0x0001
            checksum = checksum >> 1
            if lastbit == 1:
                checksum = checksum ^ 0xA001

    lowCRC = checksum >> 8
    checksum = checksum << 8
    highCRC = checksum >> 8

    return lowCRC & 0xFF == arr[-1] and highCRC & 0xFF == arr[-2]


def cal_checksum_func(arr):
    
    checksum = 0xFFFF
    for num in range(0, len(arr)):

        lsb = arr[num] % 256
        checksum = checksum ^ lsb
        for count in range(1, 9):
            lastbit = (checksum & 0x0001) % 256
            checksum = checksum >> 1

            if lastbit == 1:
                checksum = checksum ^ 0xA001

    lowCRC = (checksum >> 8) % 256
    checksum = checksum << 8
    highCRC = (checksum >> 8) % 256

    
    return lowCRC,highCRC


def run_and_get_data():
    data = {}

    for device in SEND_CONFIG:
        RECV_LEN = device["recv_len"]
        data[device["name"]] = {}
        bytes_rec = []
        to_send = device["arr"]
        low,high = cal_checksum_func(to_send)
        to_send.append(high)
        to_send.append(low)

        try:
            ser.flushInput()
            ser.flushOutput()
            ser.write(to_send)
            ser.flush()
            bytes_rec = ser.read(RECV_LEN)
        except:
            bytes_rec = bytearray([0] * RECV_LEN)

        print("________RECIEVED_______: ", bytes_rec)
        if len(bytes_rec) < RECV_LEN:
            bytes_rec = bytearray([0] * RECV_LEN)

        if not checksum_func(bytes_rec):
            bytes_rec = bytearray([0] * RECV_LEN)

        vals = compute_float(bytes_rec)
        for i, variable in enumerate(device["vars"]):
            data[device["name"]][variable] = vals[i]

    return data


def run_serial():
    try:
        global ser
        ser.baudrate = 9600
        ser.port = "COM" + COM_PORT
        ser.timeout = 0.7
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.bytesize = serial.EIGHTBITS
        ser.open()
        time.sleep(0.5)
        return "true"
    except:
        try:
            ser.inWaiting()
            return "true"
        except:
            if ser:
                ser.close()
            return "false"


def get_dates(start_date, end_date):
    sdate = datetime.datetime.strptime(start_date, "%Y-%m-%d")  # start date
    edate = datetime.datetime.strptime(end_date, "%Y-%m-%d")  # end date
    delta = edate - sdate  # as timedelta
    lst = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        lst.append(day.strftime("%Y-%m-%d"))

    return lst


@app.route("/data")
def data():
    def dataStream():
        while True:
            data = run_and_get_data()
            yield "data: " + json.dumps(data) + "\n\n"
            time.sleep(0.1)

    return Response(dataStream(), mimetype="text/event-stream")
   

@app.route("/mock_data", methods=["GET"])
def mock_data():
    if request.method == "GET":
        return jsonify(
            {
                1: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                    "V3": random.randint(100, 9999),
                    "V4": random.randint(100, 9999),
                    "V5": random.randint(100, 9999),
                    "V6": random.randint(100, 9999),
                    "V7": random.randint(100, 9999),
                    "V8": random.randint(100, 9999),
                    "V9": random.randint(100, 9999),
                    "V10": random.randint(100, 9999),
                    "V11": random.randint(100, 9999),
                    "V12": random.randint(100, 9999),
                    "V13": random.randint(100, 9999),
                    "V14": random.randint(100, 9999),
                    "V15": random.randint(100, 9999),
                    "V16": random.randint(100, 9999),
                    "V17": random.randint(100, 9999),
                    "V18": random.randint(100, 9999),
                    "V19": random.randint(100, 9999),
                    "V20": random.randint(100, 9999),
                },
                2: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                    "V3": random.randint(100, 9999),
                    "V4": random.randint(100, 9999),
                    "V5": random.randint(100, 9999),
                    "V6": random.randint(100, 9999),
                    "V7": random.randint(100, 9999),
                    "V8": random.randint(100, 9999),
                    "V9": random.randint(100, 9999),
                    "V10": random.randint(100, 9999),
                    "V11": random.randint(100, 9999),
                    "V12": random.randint(100, 9999),
                    "V13": random.randint(100, 9999),
                    "V14": random.randint(100, 9999),
                    "V15": random.randint(100, 9999),
                    "V16": random.randint(100, 9999),
                    "V17": random.randint(100, 9999),
                    "V18": random.randint(100, 9999),
                    "V19": random.randint(100, 9999),
                    "V20": random.randint(100, 9999),
                },
                3: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                },
                4: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                },
                5: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                },
                6: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                },
                7: {
                    "V1": random.randint(100, 9999),
                    "V2": random.randint(100, 9999),
                },
            }
        )


def get_message():
    """this could be any function that blocks until data is ready"""
    time.sleep(2.0)
    s = time.ctime(time.time())
    return s


@app.route("/stream")
def stream():
    def eventStream():
        while True:
            # wait for source data to be available, then push it
            yield "data: {}\n\n".format(get_message())

    return Response(eventStream(), mimetype="text/event-stream")


@app.route("/connected", methods=["GET", "POST", "DELETE"])
def connected():
    global start
    start = False
    if request.method == "GET":
        return run_serial()


@app.route("/mock_connected", methods=["GET", "POST", "DELETE"])
def mock_connected():
    global start
    start = False
    if request.method == "GET":
        return "true"


if __name__ == "__main__":
    ui.run()
