import json
import time
import datetime
import sys
import select
import serial
import threading

# Global flag to end the timer
stop_flag = threading.Event()
buffer = {}

def start_reading(timer, buffer, date_time):
    print("in the function start reading")
    print(buffer)
    
    end_time = time.time() + int(timer)*60
    
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
            if stop_flag.is_set():  # Check if stop flag is set
                print("Timer stopped")
                break
            
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
            
            time.sleep(1)
        
        buffer["DataSourceStatus"] = "Certi Tester"
    
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Falling back to simulated data")
        while time.time() < end_time:
            if stop_flag.is_set():  # Check if stop flag is set
                print("Timer stopped")
                break
            
            # Simulate reading data
            print(time.time())
            time.sleep(1)  # Sleep to prevent busy-waiting
        
        test_type = buffer['TestType']
        file_name = ""
        
        if test_type == 'G':
            file_name = 'GravimetricTest.json'
        elif test_type == 'P':
            file_name = 'PenetrationTest.json'
        else:
            file_name = 'LoadingTest.json'
        
        with open(f'./fake_data_source_local/{file_name}', 'r') as file:
            data = json.load(file)    
        
        buffer['Data'] = data['Data']
          
        buffer["DataSourceStatus"] = "Using old data files. Also simulating time loop"            
        

    print("Timer completed")
    print(buffer)
    
    return buffer



def buffer_initialization(meta_data):    
    
    global stop_flag
    
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
    
    timer = meta_data['minutes']
    
    # Reset stop flag before starting the timer
    stop_flag.clear()
    
    update_buffer = start_reading(timer, buffer, date_time)
    
    return update_buffer


def end_reading():
    global stop_flag
    stop_flag.set() 