import json
import time
import datetime
import sys
import select
import serial
import threading
import random

# Global flag to end the timer
stop_flag = threading.Event()
live_data = []
is_reading_active = False

def start_reading(timer, buffer, date_time):
    global live_data, is_reading_active 
    print("in the function start reading")
    print(buffer)
    
    # If timer is provided, calculate the end_time; else, run infinitely
    if timer:
        end_time = time.time() + int(timer) * 60
    else:
        end_time = None  # No end time, run indefinitely

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
        
        is_reading_active = True
        
        while end_time is None or time.time() < end_time:
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
                    live_data.append(certiString[:-2] + date_string)
                else:
                    buffer["Data"].append(certiString[:-2])
                    live_data.append(certiString[:-2])
            
            time.sleep(1)
        
        buffer["DataSourceStatus"] = "Certi Tester"
    
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Falling back to simulated data")
        
        is_reading_active = True
        
        while end_time is None or time.time() < end_time:
            if stop_flag.is_set():  # Check if stop flag is set
                print("Timer stopped")
                break
            
            # Simulate reading data
            print("time: ",  time.time())
                    
            delay = random.uniform(0, 10)
            time.sleep(delay) 
            
            #f_time = time.time() - 1
            #p_time = time.time() + 1
            #current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            live_data.append("GARBAGE")
        
        test_type = buffer['TestType']
        file_name = ""
        
        if test_type == 'G':
            file_name = 'GravimetricTest.json'
        elif test_type == 'P':
            file_name = 'PenetrationTest.json'
        else:
            file_name = 'LoadingTest.json'
                         
        # overwrite the data    
        with open(f'./fake_data_source_local/{file_name}', 'r') as file:
            data = json.load(file)    
            
        buffer['Data'] = data['Data']
            
        buffer["DataSourceStatus"] = "Using old data files. Also simulating time loop"            
    
    is_reading_active = False    

    print("Timer completed")
    print(buffer)
    
    return buffer


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

def connect_certi_tester(meta_data): 
    
    global stop_flag
    stop_flag.clear()
    
    # before the buffer initialzation we clear the live data
    global live_data
    live_data = []
    
    # NO matter what, buffer needs to be initalized
    # Even if starting for x minutes or infinite
    
    buffer, date_time = buffer_initialization(meta_data)
   
    # if minutes is given, then we immediatly start reading.    
    if 'minutes' in meta_data:   
        timer = meta_data['minutes']
        print(timer)
        # Reset stop flag before starting the timer
        update_buffer = start_reading(timer, buffer, date_time)
        return update_buffer

    else:
        print("timer")
        return buffer, date_time
    

def end_reading():
    global stop_flag
    global is_reading_active
    #is_reading_active = False
    stop_flag.set() 
    
def get_live_data():
    global live_data
    #print("live_data:", live_data)
    return live_data