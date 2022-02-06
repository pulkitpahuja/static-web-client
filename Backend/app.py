from flask import Flask, render_template, Response, request, redirect, url_for,jsonify,send_from_directory
import json
from flask_cors import CORS
from webui import WebUI
import serial
import sys
import os
import random
import time
import csv
from dateutil.parser import parse
from xlsxwriter.workbook import Workbook

import threading
import struct
import datetime
from fpdf import FPDF, HTMLMixin
from datetime import date, timedelta
from constants import SEND_BYTES,RECV_LENGTH
class HTML2PDF(FPDF, HTMLMixin):
    pass

global start 

ser=0

app = Flask(__name__, static_url_path='', static_folder='build')
ui = WebUI(app, debug=True) 
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  '''Return index.html for all non-api routes'''
  if path != "" and os.path.exists(f"{app.static_folder}/{path}"):
        return send_from_directory(app.static_folder, path)
  else:
    return send_from_directory(app.static_folder, 'index.html')
   
def compute_float(bytes_rec):

    if (len(bytes_rec)==17):
        list1=[[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]],[bytes_rec[8],bytes_rec[7],bytes_rec[10],bytes_rec[9]],[bytes_rec[12],bytes_rec[11],bytes_rec[14],bytes_rec[13]]]
        final_val=list(struct.unpack('<f', bytearray(list1[0])))
        final_val1=list(struct.unpack('<f', bytearray(list1[1])))
        final_val2=list(struct.unpack('<f', bytearray(list1[2])))
        return [round(final_val[0],2),round(final_val1[0],2),round(final_val2[0],2)]

    if (len(bytes_rec)==13):
        list1=[[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]],[bytes_rec[8],bytes_rec[7],bytes_rec[10],bytes_rec[9]]]
        final_val=list(struct.unpack('<f', bytearray(list1[0])))
        final_val1=list(struct.unpack('<f', bytearray(list1[1])))
        return [round(final_val[0],2),round(final_val1[0],2)]

    else:
        list1=[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]]

        final_val=list(struct.unpack('<f', bytearray(list1)))
        return round(final_val[0],2)

def checksum_func(bytearray):
    checksum=(0xffff)
    for num in range(0,len(bytearray)-2):
        lsb=bytearray[num]
        checksum=(checksum^lsb)
        for count in range(1,9):    
            lastbit=checksum&0x0001
            checksum=checksum>>1
            if (lastbit==1):        
                checksum=checksum^0xa001
    
    lowCRC = checksum>>8
    checksum = checksum<<8
    highCRC = checksum>>8
      
    return(lowCRC,highCRC)

def cal_checksum_func(arr):

    checksum=(0xffff)
    for num in range(0,len(arr)):

        lsb=arr[num] % 256
        checksum=(checksum^lsb)
        for count in range(1,9):
            lastbit=(checksum&0x0001)% 256
            checksum=checksum>>1

            if (lastbit==1):
                checksum=checksum^0xa001

    lowCRC = (checksum>>8)% 256
    checksum = checksum<<8
    highCRC = (checksum>>8)% 256
    return(lowCRC,highCRC)

def run_and_get_data():
    ser.flushInput()
    ser.flushOutput()
    ser.write(SEND_BYTES)   
    ser.flush()  
    time.sleep(.6)
    bytes_rec=ser.read(RECV_LENGTH)
    if (len(bytes_rec)<RECV_LENGTH):
        bytes_rec=bytearray(RECV_LENGTH)

    low,high=checksum_func(bytes_rec)

    if (low&0xff==bytes_rec[-1] and high&0xff==bytes_rec[-2]):
        final_rec=bytes_rec
        print("CHECKSUM MATCHED")        
    else:
        new_byte=bytearray(RECV_LENGTH)
        final_rec=new_byte

    vals = compute_float(final_rec)
    return vals
            
def run_serial(com):
    try:
        global ser
        ser = serial.Serial("COM"+com, 9600,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,timeout=1)
        time.sleep(.5)
        return "true"
    except :
        try:
            ser.inWaiting()
            return "true"
        except:
            if(ser):
                ser.close()
            return "false"
    
def get_dates(start_date,end_date):
    sdate = datetime.datetime.strptime(start_date, '%Y-%m-%d')   # start date
    edate =datetime.datetime.strptime(end_date, '%Y-%m-%d')   # end date
    delta = edate - sdate       # as timedelta
    lst = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        lst.append(day.strftime('%Y-%m-%d'))
    
    return lst

@app.route('/get_data',methods = ['GET'])
def get_fac_data():
   if request.method == 'GET':
       return run_and_get_data()
    
@app.route('/connected',methods = ['GET', 'POST', 'DELETE'])
def connected():
    global start
    start = False
    if request.method == 'POST':
        data =request.form.to_dict()
        return run_serial(data["com_port"])
     
if __name__ == "__main__":
    ui.run()        
        

        