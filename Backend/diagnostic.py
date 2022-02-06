from flask import Flask, render_template, Response, request, redirect, url_for,jsonify
import serial
import json
from webui import WebUI
import serial
import sys
import os
import random
import time
import csv

import threading
import struct
import datetime
from fpdf import FPDF, HTMLMixin

byte_val={
         "1":bytearray([0x03,0x03,000,000,000,0x04,0x45,0xeb]),
         "2":bytearray([0x07,0x03,000,000,000,0x02,0xc4,0x6d]),
         "3":bytearray([0x09,0x03,000,000,000,0x02,0xc5,0x43]),
         "4":bytearray([0x01,0x03,000,000,000,0x02,0xc4,0x0b]),
         "5":bytearray([0x0b,0x03,000,000,000,0x06,0xc5,0x62]),
         "6":bytearray([0x02,0x03,000,000,000,0x02,0xc4,0x38]),
         "7":bytearray([0x04,0x03,000,000,000,0x02,0xc4,0x5e]),
         "8":bytearray([0x05,0x03,000,000,000,0x02,0xc5,0x8f]),
         "9":bytearray([0x08,0x03,000,000,000,0x02,0xc4,0x92]),
         "10":bytearray([0x06,0x03,000,000,000,0x02,0xc5,0xbc]),
        }

to_on_write=bytearray([byte_val["4"][0],0x03,155,000,000,0x04])
to_off_write=bytearray([byte_val["4"][0],0x03,215,000,000,0x04])

global ser
ser = serial.Serial("COM3",9600,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,timeout=.3)

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

def on_relay():
    low,high=cal_checksum_func(to_on_write)
    to_on_write.append(high)
    to_on_write.append(low)
    ser.write(to_on_write)
    print("RELAY ON")


def off_relay():
    low,high=cal_checksum_func(to_off_write)
    to_off_write.append(high)
    to_off_write.append(low)   
    ser.write(to_off_write) 
    print("RELAY OFF",to_off_write)


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

on_relay()

time.sleep(3)
off_relay()
time.sleep(.5)

ser.write(byte_val["2"])
ser.flush()
time.sleep(.4)

bytes_rec = ser.read(9)
import re
print(bytes_rec )

low,high=checksum_func(bytes_rec)
print(low,high)
if (low&0xff==bytes_rec[8] and high&0xff==bytes_rec[7]):
    print("CHECKSUM MATCHED")
list1=[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]]
final_val=list(struct.unpack('<f', bytearray(list1)))
print(final_val)
