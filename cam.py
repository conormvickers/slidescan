import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import serial
import time
import re
import signal
import sys


# Create a flag to indicate that the threads should stop
stop_event = threading.Event()

# List to store the running threads
threads = []



absolute_preable = b"G90 G0"    
start_position = [-5.2, -2, 7]
scan_start_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2])
# Create the main window
root = tk.Tk()
root.title("USB Camera with GUI")

# Create a label to display the video feed
video_label = tk.Label(root)
video_label.pack()

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack()

def button1_click():
    print("Button 1 clicked!")
    test_command = b'$?\n'  # Send the '$I' command to get the GRBL settings
    send_gcode(test_command)

button1 = tk.Button(button_frame, text="Button 1", command=button1_click)
button1.pack(side=tk.LEFT)

def button2_click():
    print("Button 2 clicked!")
    test_command = b'?\n'  
    send_gcode(test_command)

def home_click():
    print("Home clicked!")
    homecommand = b'$H\n'  
    print(homecommand)
    threading.Thread(target=send_gcode, args=(homecommand, None)).start()
    

def zero_click():
    print("Zero clicked!")
    test_command = absolute_preable + b' X0 Y0 Z0\n'  
    send_gcode(test_command)
    
def zoom_click():
    print("Zoom clicked!")
    test_command = absolute_preable + scan_start_position.encode()
    send_gcode(test_command)
    
zoom_above_start = 0
scan_x = 0
scan_y = 0
save_next_frame = False
record_variance_next_frame = False
highest_variance = 0
highest_variance_z = 0

step_size = 0.05
zstep_size = 0.1

in_startup_sequence = True
startup_sequence_index = 0



def get_scan_position(i, j):
    global save_next_frame, scan_x, scan_y, zoom_above_start
    positionbinary = ("X{} Y{} Z{}\n".format(start_position[0] + step_size * i, start_position[1] + step_size * j, start_position[2] + + zoom_above_start)).encode()
    return positionbinary


    
def start_scan():
    global save_next_frame, scan_x, scan_y, zoom_above_start
    print("Start Scan clicked!")
    for scan_x in range(4):
        for scan_y in range(4):
            thisposition = get_scan_position(scan_x, scan_y)
            test_command = absolute_preable + thisposition
            send_gcode(test_command)
            save_next_frame = True
            time.sleep(2)

def variance_callback():
    global record_variance_next_frame
    
    record_variance_next_frame = True
    time.sleep(1)
            

def zoom_in():
    print("Zoom In clicked!")
    global zoom_above_start
    zoom_above_start = zoom_above_start + zstep_size
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + zoom_above_start).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode(test_command, variance_callback)

def zoom_out():
    print("Zoom Out clicked!")
    global zoom_above_start
    zoom_above_start = zoom_above_start - zstep_size
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + zoom_above_start).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode(test_command, variance_callback)

def startup_sequence():
    global in_startup_sequence, startup_sequence_index
    startup_commands[startup_sequence_index]()    

def go_above_best_zoom():
    global highest_variance_z, zstep_size
    print("Go above best zoom clicked!", highest_variance_z, zstep_size, ( 5 * zstep_size))
    zoom_above_start = highest_variance_z - ( 5 * zstep_size)
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + zoom_above_start ).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode(test_command)
    
def zoom_to_best_zoom():
    global highest_variance_z
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + highest_variance_z ).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode(test_command)
    
def shrink_z_step():
    global zstep_size, startup_sequence_index, startup_commands, zoom_above_start
    zoom_above_start = highest_variance_z - ( 3 * zstep_size)
    zstep_size = zstep_size / 2
    startup_sequence_index = startup_sequence_index + 1
    startup_commands[startup_sequence_index]()
    
def zoom_till_good_enough():
    global zoom_above_start
    print("Zoom till good enough clicked!")
    zoom_above_start = zoom_above_start + zstep_size
    zoom_to_position = "X {} Y{} Z{}\n".format(start_position[0], start_position[1], start_position[2] + zoom_above_start).encode()
    test_command = absolute_preable + zoom_to_position
    send_gcode(test_command, variance_callback)
 
startup_commands = [
    home_click,
    zoom_click, 
    zoom_in,
    
    zoom_click,
    shrink_z_step, 
    
    go_above_best_zoom,
    zoom_to_best_zoom, 
    start_scan
]        

startbutton = tk.Button(button_frame, text="Start", command=startup_sequence)
startbutton.pack(side=tk.LEFT)   

button2 = tk.Button(button_frame, text="Button 2", command=button2_click)
button2.pack(side=tk.LEFT)

homebutton = tk.Button(button_frame, text="Home", command=home_click)
homebutton.pack(side=tk.LEFT)

zerobutton = tk.Button(button_frame, text="Zero", command=zero_click)
zerobutton.pack(side=tk.LEFT)

zoombutton = tk.Button(button_frame, text="Zoom", command=zoom_click)
zoombutton.pack(side=tk.LEFT)

zoominbutton = tk.Button(button_frame, text="Zoom In", command=zoom_in)
zoominbutton.pack(side=tk.LEFT)

zoomoutbutton = tk.Button(button_frame, text="Zoom Out", command=zoom_out)
zoomoutbutton.pack(side=tk.LEFT)

scanbutton = tk.Button(button_frame, text="Start Scan", command=start_scan)
scanbutton.pack(side=tk.LEFT)

exceptionthrown = False

def close_all():
    
    global cap, ser, root, exceptionthrown
    root.destroy()
    exceptionthrown = True

    for thread in threads:
        print("Interrupting thread")
        thread.join()
    
    

    
close_button = tk.Button(button_frame, text="Close", command=close_all)
close_button.pack(side=tk.LEFT)

# Establish serial connection with GRBL controller
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=3)  # Replace '/dev/ttyUSB0' with your actual serial port
    print("Serial connection established with GRBL controller")
except serial.SerialException:
    print("Failed to establish serial connection with GRBL controller")
    
def send_gcode(gcode, callback=None):
    global in_startup_sequence, startup_sequence_index, startup_commands, zoom_above_start
    ser.write(gcode)
    response = ser.readline()
    while not re.search(b"ok\n?", response): #response != b'':  # wait for 'ok' response from GRBL
        response = ser.readline()
        print("Response: ", response)
        if response:
            print(response.decode())
    print("Done")
    if callback:
        print("Running callback")
        callback()
        
    if in_startup_sequence:
        startup_sequence_index = startup_sequence_index + 1
        if startup_sequence_index >= len(startup_commands):
            in_startup_sequence = False
        else:
            print("Running startup command: ", zoom_above_start)
            startup_commands[startup_sequence_index]()
        
    
def update_video():
    global exceptionthrown, save_next_frame, scan_x, scan_y, record_variance_next_frame, zoom_above_start, highest_variance, highest_variance_z
    
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame")
            i = 0
            while not ret and not exceptionthrown:
                if i > 4:
                    exceptionthrown = True
                    break
                print('waiting few seconds  ...  ', i)
                time.sleep(1)
                print("trying again")
                cap = cv2.VideoCapture(1)

                ret, frame = cap.read()
                i = i + 1
    except Exception as e:
        print("Error updating video feed:", e)
        exceptionthrown = True
        
    cv2.namedWindow("Video Feed", cv2.WINDOW_NORMAL)
    
    while not exceptionthrown:
        
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Video Feed", frame)
            if save_next_frame:
                cv2.imwrite("{}-{}.jpg".format(scan_x, scan_y), frame)
                save_next_frame = False
                
            if record_variance_next_frame:
                record_variance_next_frame = False
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Calculate the variance of the Laplacian
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                variance = laplacian.var()
                print("Variance: ", variance)
                
                if variance > highest_variance:
                    highest_variance = variance
                    highest_variance_z = zoom_above_start
                    
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error reading frame")
            i = 0
            while not ret and not exceptionthrown:
                if i > 4:
                    exceptionthrown = True
                    break
                print('waiting few seconds  ...  ', i)
                time.sleep(1)
                print("trying again")
                cap = cv2.VideoCapture(1)

                ret, frame = cap.read()
                i = i + 1
    print("Video feed closed")
    cv2.destroyAllWindows()
    cap.release()


        

# Create a thread for the video feed update loop
def start_video_thread():
    try:
        video_thread = threading.Thread(target=update_video)
        video_thread.start()
        threads.append(video_thread)
        print("Video thread started")
    except Exception as e:
        print("Error starting video thread:", e)
        root.destroy()

# Create a thread for the video feed update loop
# start_video_thread()

# Start the Tkinter event loop
root.mainloop()

# Close the serial connection when the window is closed
try:
    ser.close()
    print("Serial connection closed")
except NameError:
    pass