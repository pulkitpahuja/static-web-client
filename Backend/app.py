import random
from flask import (
    Flask,
    render_template,
    Response,
    request,
    redirect,
    url_for,
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
from dateutil.parser import parse
from xlsxwriter.workbook import Workbook

import struct
import datetime
from fpdf import FPDF, HTMLMixin
from datetime import date, timedelta
from constants import SEND_CONFIG

ser = 0


class HTML2PDF(FPDF, HTMLMixin):
    pass


global start
try:
    f = open("config.json")
    config = json.load(f)
    COM_PORT = config["COM_PORT"]
except:
    sys.exit(
        "Configurtion file not found. Please check the config.json file. Exiting..."
    )


print(COM_PORT)

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

    if len(bytes_rec) == 17:
        list1 = [
            [bytes_rec[4], bytes_rec[3], bytes_rec[6], bytes_rec[5]],
            [bytes_rec[8], bytes_rec[7], bytes_rec[10], bytes_rec[9]],
            [bytes_rec[12], bytes_rec[11], bytes_rec[14], bytes_rec[13]],
        ]
        final_val = list(struct.unpack("<f", bytearray(list1[0])))
        final_val1 = list(struct.unpack("<f", bytearray(list1[1])))
        final_val2 = list(struct.unpack("<f", bytearray(list1[2])))
        return [
            round(final_val[0], 2),
            round(final_val1[0], 2),
            round(final_val2[0], 2),
        ]

    if len(bytes_rec) == 13:
        list1 = [
            [bytes_rec[4], bytes_rec[3], bytes_rec[6], bytes_rec[5]],
            [bytes_rec[8], bytes_rec[7], bytes_rec[10], bytes_rec[9]],
        ]
        final_val = list(struct.unpack("<f", bytearray(list1[0])))
        final_val1 = list(struct.unpack("<f", bytearray(list1[1])))
        return [round(final_val[0], 2), round(final_val1[0], 2)]

    else:
        list1 = [bytes_rec[4], bytes_rec[3], bytes_rec[6], bytes_rec[5]]

        final_val = list(struct.unpack("<f", bytearray(list1)))
        return round(final_val[0], 2)


def checksum_func(bytearray):
    checksum = 0xFFFF
    for num in range(0, len(bytearray) - 2):
        lsb = bytearray[num]
        checksum = checksum ^ lsb
        for count in range(1, 9):
            lastbit = checksum & 0x0001
            checksum = checksum >> 1
            if lastbit == 1:
                checksum = checksum ^ 0xA001

    lowCRC = checksum >> 8
    checksum = checksum << 8
    highCRC = checksum >> 8

    return (lowCRC, highCRC)


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
    return (lowCRC, highCRC)


def run_and_get_data():
    data = {}
    for device in SEND_CONFIG:
        RECV_LEN = device["recv_len"]
        ser.flushInput()
        ser.flushOutput()
        ser.write(device["arr"])
        ser.flush()
        time.sleep(0.6)
        bytes_rec = ser.read(RECV_LEN)
        if len(bytes_rec) < RECV_LEN:
            bytes_rec = bytearray(RECV_LEN)

        low, high = checksum_func(bytes_rec)

        if low & 0xFF == bytes_rec[-1] and high & 0xFF == bytes_rec[-2]:
            final_rec = bytes_rec
            print("CHECKSUM MATCHED")
        else:
            new_byte = bytearray(RECV_LEN)
            final_rec = new_byte

        vals = compute_float(final_rec)
        for i, variable in enumerate(device["vars"]):
            data[device["name"]][variable] = vals[i]

    return data


def run_serial():
    try:
        global ser
        ser = serial.Serial(
            COM_PORT,
            9600,
            serial.EIGHTBITS,
            serial.PARITY_NONE,
            serial.STOPBITS_ONE,
            timeout=1,
        )
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


@app.route("/data", methods=["GET"])
def data():
    if request.method == "GET":
        return run_and_get_data()


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
