import serial
import json
import time
import datetime
import sys
import select



def buffer_initialization(meta_data):    
    date_time = False

    initial_weight = None
    final_weight = None

    if meta_data['testType'] == "G":
        initial_weight = float(meta_data['initialWeight'])
    elif meta_data['testType'] == 'P':
        date_time = True
    
    buffer = {"TestType": meta_data['testType'], "Operator": meta_data['operatorName'], "Notes": meta_data['notes'],
                "InitialWeight": initial_weight, "FinalWeight": final_weight, "Data": []
                }
    print(buffer)
    return buffer, date_time


def start_reading(timer, buffer, date_time):
    print("in the function start reading")
    print(buffer)
    
    end_time = time.time() + timer
    
    try:
        serialPort = serial.Serial(
            port="/dev/ttyUSB0",
            baudrate=9600,
            bytesize=serial.SEVENBITS,
            timeout=2,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_ODD,
            rtscts=True,
            dsrdtr=True)
        
        while time.time() < end_time:
            # Wait until there is data waiting in the serial buffer
            if serialPort.in_waiting > 0:
                # Read data out of the buffer until a carriage return / new line is found
                serialString = serialPort.readline()
                certiString = serialString.decode()
                print(certiString, end="")
                
                if date_time:  # append a date time
                    current_time = datetime.datetime.now()
                    date_string = current_time.strftime(" %m %d %Y %H %M %S")
                    buffer["Data"].append(certiString[:-2] + date_string)
                else:
                    buffer["Data"].append(certiString[:-2])
            
            buffer["Data"].append("Mission successful, python script inside docker container, can access the port, not sure about reading")

            time.sleep(1)
    
    except Exception as e:
        buffer["Data"].append("This is simulated data couldn't connect to device")
        print(f"Error occurred: {e}")
        print("Falling back to simulated data")
        while time.time() < end_time:
            # Simulate reading data
            buffer["Data"].append(time.time())
            print(time.time())
            time.sleep(1)  # Sleep to prevent busy-waiting
            
        

    print("Timer completed")
    print(buffer)
    
    return buffer
