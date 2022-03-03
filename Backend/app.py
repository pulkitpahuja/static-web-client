import random
from flask import (
    Flask,
    request,
    Response,
    jsonify,
    send_from_directory,
)
from werkzeug.serving import WSGIRequestHandler
import json, os, signal
from flask_cors import CORS
from webui import WebUI
import serial
import sys
import time

import struct
import datetime
from datetime import date, timedelta
from constants import SEND_CONFIG

ser = serial.Serial()
overall_state = False
try:
    f = open("config.json")
    config = json.load(f)
    COM_PORT = config["COM_PORT"]
except:
    sys.exit(
        "Configurtion file not found. Please check the config.json file. Exiting..."
    )

WSGIRequestHandler.protocol_version = "HTTP/1.1"
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

    return lowCRC, highCRC


def findElementOnDeviceID(id):
    copy = {}
    for x in SEND_CONFIG:
        if x["arr"][0] == id:
            copy = {**x}
            break
        else:
            x = None

    return copy


def run_and_get_data():
    data = {}

    for device in SEND_CONFIG:
        RECV_LEN = device["recv_len"]
        data[device["name"]] = {}
        bytes_rec = []
        to_send = []
        to_send = device["arr"]
        if to_send[0] == 0x05:
            ac_1 = findElementOnDeviceID(0x01)
            ac_2 = findElementOnDeviceID(0x02)
            dc_1 = findElementOnDeviceID(0x03)
            dc_2 = findElementOnDeviceID(0x04)
            ac_1_val = data[ac_1["name"]][ac_1["vars"][0]]
            ac_2_val = data[ac_2["name"]][ac_2["vars"][0]]
            dc_1_val = data[dc_1["name"]][dc_1["vars"][0]]
            dc_2_val = data[dc_2["name"]][dc_2["vars"][0]]
            data[device["name"]]["Eff1"] = (dc_1_val * 100) / ac_1_val if ac_1_val != 0 else "-"
            data[device["name"]]["Eff2"] = (ac_2_val * 100) / dc_2_val if dc_2_val != 0 else "-"
            continue
        try:
            ser.flushInput()
            ser.flushOutput()
            ser.write(to_send)
            ser.flush()
            bytes_rec = ser.read(RECV_LEN)
        except:
            time.sleep(0.5)
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


@app.route("/exit_prog", methods=["GET", "POST", "DELETE"])
def exit_prog():
    if request.method == "GET":
        sig = getattr(signal, "SIGKILL", signal.SIGTERM)
        os.kill(os.getpid(), sig)
        return "Killed"


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
