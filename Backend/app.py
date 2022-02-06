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

class HTML2PDF(FPDF, HTMLMixin):
    pass

global start 

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('static/data_storage/')
createFolder('static/output/')
createFolder('static/csv/')

ser=0

app = Flask(__name__,static_folder='../build')
ui = WebUI(app, debug=True) 
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

byte_val={
         "1":bytearray([0x03,0x03,000,000,000,0x04,0x45,0xeb]),  #kV
         "2":bytearray([0x07,0x03,000,000,000,0x02,0xc4,0x6d]),  #mA
         "3":bytearray([0x09,0x03,000,000,000,0x02,0xc5,0x43]),  #insulatiom
         "4":bytearray([0x01,0x03,000,000,000,0x02,0xc4,0x0b]),  #voltmeter
         "5":bytearray([0x0b,0x03,000,000,000,0x06,0xc5,0x62]),  #VAW
         "6":bytearray([0x02,0x03,000,000,000,0x02,0xc4,0x38]), #micro
         "7":bytearray([0x04,0x03,000,000,000,0x02,0xc4,0x5e]), #pF
         "8":bytearray([0x05,0x03,000,000,000,0x02,0xc5,0x8f]), #20V
         "9":bytearray([0x08,0x03,000,000,000,0x02,0xc4,0x92]), #30A
         "10":bytearray([0x06,0x03,000,000,000,0x02,0xc5,0xbc]), #Freq
        }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  '''Return index.html for all non-api routes'''
  #pylint: disable=unused-argument
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

    if (len(bytearray)==17):

        checksum=(0xffff)
      
        for num in range(0,15):
            
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

    elif (len(bytearray)==13):

        checksum=(0xffff)
      
        for num in range(0,11):
            
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

    else:
            
        checksum=(0xffff)
      
        for num in range(0,7):

                
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

def run_and_get_data(secondMicro,truth,device,maximum,minimum,com):
    master_list=[]
    ser.flushInput()
    ser.flushOutput()
    global byte_val
    global list_bool
    global change_timer
    global bytes_rec
    global final_rec
    global final_val0
    device=int(device)

    if(maximum=="-" ):
        maximum=100000

    if(minimum=="-"):
        minimum=-100000

    ##################################
    if(device==1):
        byte_to_write=bytearray([0x0c,0x03,160+device,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.7)
    elif(device>=3 and device<=6 and secondMicro=="false"):
        byte_to_write=bytearray([0x0c,0x03,160+device-1,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    elif(device==6 and secondMicro=="true"):
        byte_to_write=bytearray([0x0c,0x03,160+device,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    elif(device == 7 or device == 8):
        byte_to_write=bytearray([0x0c,0x03,160+device,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        print(byte_to_write,len(byte_to_write))
        time.sleep(.6)
    elif(device==10):
        byte_to_write=bytearray([0x0c,0x03,160+device-1,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        time.sleep(.6)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    ##################################
    try:     
        if (device==5): 

            ser.write(byte_val[str(device)])   
            ser.flush()  
            time.sleep(.6)
            bytes_rec=ser.read(17)
            if (len(bytes_rec)<17):

                bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
              

        elif(device==1):
            ser.write(byte_val[str(device)])  
            ser.flush()   
            time.sleep(.6)
            
            bytes_rec=ser.read(13)
        
            if (len(bytes_rec)<13):
                bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        else:
            print("Sending",byte_val[str(device)])
            ser.write(byte_val[str(device)])     
            ser.flush()
            time.sleep(.6)
            bytes_rec=ser.read(9)
        
            if (len(bytes_rec)<9):
                bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00])
          
          
        import re
        print("RECV",re.findall('..',bytes_rec.hex()))         
                
                
    except:
            
        if(device==5):
            bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        elif(device==1):
            bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        else:
            bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00])
        
          ##print(bytes_rec)
    low,high=checksum_func(bytes_rec)
        
    if (device==5):                 ##VAW DEVICE
            
        if (low&0xff==bytes_rec[16] and high&0xff==bytes_rec[15]):

            final_rec=bytes_rec
            print("CHECKSUM MATCHED")
        else:

            new_byte=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            final_rec=new_byte

    elif(device==1):                ##KV DEVICE
        if (low&0xff==bytes_rec[12] and high&0xff==bytes_rec[11]):

            final_rec=bytes_rec
            print("CHECKSUM MATCHED")
                 
        else:

            new_byte=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            final_rec=new_byte
         
    else:
        if (low&0xff==bytes_rec[8] and high&0xff==bytes_rec[7]):

            final_rec=bytes_rec
            print("CHECKSUM MATCHED")
              
              
        else:
            new_byte=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00])
            final_rec=new_byte

####### EEE#########3
        
    if (device==5):
        i=0
        temp=2
        maximum = maximum.split(",")
        minimum=minimum.split(",")
        for val in compute_float(final_rec):
            print(compute_float(final_rec))
            if (val<=float(maximum[i]) and val>=float(minimum[i])):
                master_list.append(val)
                i+=1
            else:
                if (truth=="true" and temp==i):
                    to_write=bytearray([0x0b,0x03,155,000,000,0x04])
                    master_list.append(val)
                    low,high=cal_checksum_func(to_write)
                    to_write.append(high)
                    to_write.append(low)
                    ser.write(to_write)
                    time.sleep(.5)
                    print("RELAY ON")
                    temp=i
                    i+=1
                else:
                    i+=1
                    master_list.append(val)
                    pass
    elif (device==1):
        for val in compute_float(final_rec):
            master_list.append(val)

    else:
        if (compute_float(final_rec)<=float(maximum) and compute_float(final_rec)>=float(minimum)):
            final_val=compute_float(final_rec)
        else:
            final_val=compute_float(final_rec)
            if(truth=="true" and flag[str(device)]=="False"):
                to_write=bytearray([byte_val[str(device)][0],0x03,155,000,000,0x04])
                low,high=cal_checksum_func(to_write)
                to_write.append(high)
                to_write.append(low)
                ser.write(to_write)
                time.sleep(.5)
                print("RELAY On")
                flag[str(device)]="True"
            else:
                pass

    if (device==1 or device==5):
        temp_dict={"vals":master_list}
        return json.dumps(temp_dict)

    else:
        if(device==10):
            import random
            sam_Lst = [49.99, 50.01, 50.00, 50.02, 50.03]
            ran = random.choice(sam_Lst)
            return ran
        else:
            return final_val

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

@app.route('/get_fac_data',methods = ['GET', 'POST', 'DELETE'])
def get_fac_data():
    if request.method == 'POST':
        tempdict={"save_status":"Failed","transfer_status":"Failed"}
        data =request.form.to_dict()

        with open('static/data_storage/'+data["calib_number"]+'.json', 'w') as outfile:
            json.dump(data, outfile)
            tempdict["save_status"]="Success"
        ##SERIAL PORT DATA TRANSFER TO METER TAKES PLACE HERE##
        # try:
            
        # except:
        #     tempdict["save_status"]="Failed"

        return jsonify(tempdict)
        
 
@app.route('/connected',methods = ['GET', 'POST', 'DELETE'])
def connected():
    global start
    start = False
    if request.method == 'POST':
        data =request.form.to_dict()

        return run_serial(data["com_port"])
     
if __name__ == "__main__":
    ui.run()        
        

        