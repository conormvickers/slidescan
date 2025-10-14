import serial

try:
    ser = serial.Serial('/dev/ttyACM1', 115200, timeout=3)  # Replace '/dev/ttyUSB0' with your actual serial port
    print("Serial connection established with GRBL controller")
except serial.SerialException:
    print("Failed to establish serial connection with GRBL controller")
    
ser.write("?\n".encode())
   
# Read the response
response = ser.readline()

print("Response: ", response)
while True:
    response = ser.readline()
    print("Response: ", response)
    if response:
        print(response.decode())
print("Done")