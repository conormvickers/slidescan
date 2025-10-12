import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import serial
import time
import re
import signal
import sys





absolute_preable = b"G90 G0"    
start_position = [-3.1, -8.8, 21.5]
scan_start_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2])

scan_x = 0
scan_y = 0

step_size = 0.1
zstep_size = 0.1


def send_gcode(gcode, ser):
    print("Sending G-code:", gcode.decode().strip())
    ser.write(gcode)
   
    # Read the response
    response = ser.readline()

    print("Response: ", response)
    while not re.search(b"ok\n?", response):
        response = ser.readline()
        print("Response: ", response)
        if response:
            print(response.decode())
    print("Done")

def send_gcode_wait(gcode, ser):
    print("Sending G-code:", gcode.decode().strip())
    ser.write(gcode)
    time.sleep(0.5)
    ser.write(b"G4 P0\n")
    response = ser.readline().decode().strip()
    print("Response: ", response)
    while 'ok' not in response:
        response = ser.readline().decode().strip()
        print("Response: ", response)
    print("wait confirmed: ", response)
    response = ser.readline().decode().strip()
 
    while 'ok' not in response:
        response = ser.readline().decode().strip()
        print("Response: ", response)
       
    print("Done")
  

def zero_click():
    print("Zero clicked!")
    test_command = absolute_preable + b' X0 Y0 Z0\n'  
    send_gcode(test_command)
    
def zoom_click():
    print("Zoom clicked!")
    test_command = absolute_preable + scan_start_position.encode()
    send_gcode(test_command)
 

def get_scan_position(i, j, adjustment):
    positionbinary = ("X{} Y{} Z{}\n".format(start_position[0] + step_size * i, start_position[1] + step_size * j, start_position[2] + adjustment)).encode()
    return positionbinary


    
def start_scan(bestadjustment, ser, cap):
    
    print("Start Scan clicked!")
    for scan_x in range(4):
        for scan_y in range(4):
            thisposition = get_scan_position(scan_x, scan_y, bestadjustment)
            test_command = absolute_preable + thisposition
            send_gcode_wait(test_command, ser)
            frame = get_hq_frame(cap)
            save_frame(frame, scan_x, scan_y)

def movetobest(bestadjustment, ser, cap):
    print("Moving to best adjustment:", bestadjustment)
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + bestadjustment).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode_wait(test_command, ser)
    frame = get_hq_frame(cap)
    
            

def home(ser):
    time.sleep(2)  # Wait for the serial connection to initialize
    homecommand = b'$H\n'  
    print(homecommand)
    send_gcode(homecommand, ser)

def movetostart(ser):
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] ).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode_wait(test_command, ser)
  
def get_variance(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    return variance

def save_frame(frame, x, y):
    cv2.imwrite("./images/level0/{}-{}.jpg".format(x, y), frame)
    print("Frame saved: ./images/level0/{}-{}.jpg".format(x, y))

capindex = 0
def get_frame(cap):
    global capindex
    ret, toss = cap.read()
    print("Discarded frame")
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame")
        return None
    cv2.imwrite( "frame" + str(capindex) + ".jpg", frame)
    capindex = capindex + 1
    cv2.imshow("Video Feed", frame)
    cv2.waitKey(600)
    
    return frame

def get_hq_frame(cap):
    # width = 2560  # Desired width
    # height = 1440  # Desired height
    
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame")
        return None
    cv2.imshow("Video Feed", frame)
    cv2.waitKey(100)
    return frame

def findbestzoom(ser, cap, maxtries):
    
    print("Finding best zoom")
    highest_variance = 0
    highest_variance_z = 0
    
    for i in range(maxtries):
        zoom_above_start = i * zstep_size
        zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + zoom_above_start).encode()
        test_command = absolute_preable + zoom_to_position
        send_gcode_wait(test_command, ser)
        
        frame = get_frame(cap)
        variance = get_variance(frame)
        print("Zoom level:", zoom_above_start, "Variance:", variance)
        if variance > highest_variance:
            highest_variance = variance
            highest_variance_z = zoom_above_start
    
    print("Best zoom found at Z =", highest_variance_z, "with variance =", highest_variance)
    
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error opening camera")
    exit()
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

ret, frame = cap.read()
if not ret:
    print("Error reading frame")
else: 
    print("Camera good to go")

cv2.namedWindow("Video Feed")
get_frame(cap)

time.sleep(1)
get_frame(cap)
cv2.waitKey(1000)
get_frame(cap)
cv2.waitKey(1000)
get_frame(cap)
cv2.waitKey(1000)
get_frame(cap)
cv2.waitKey(1000)
# start_scan(bestadjustment, ser, cap)

cap.release()
   