import json
import time
import datetime
import serial
import threading
import os


lock = threading.Lock()
FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'experiment_data.json')

data_structure = {
    "TestType": "",
    "Operator": "",
    "Notes": "",
    "InitialWeight": None,
    "FinalWeight": None,
    "Data": []
} 

# Function to initialize or update the experiment data in Redis
def set_experiment_data(data):
    # Store the data in Redis hash with key 'experiment'
    with lock:  # Ensure only one thread accesses this block
        with open(FILE_PATH, 'w') as file:
            print("Hi from the nuking of the file shit")
            json.dump(data, file, indent=4)
            
# Global flag to end the timer
stop_flag = threading.Event()
is_reading_active = False

def buffer_initialization(meta_data):
    #Clear old process
    global stop_flag
    stop_flag.clear()
    
    # NO matter what, buffer needs to be initalized
    # Even if starting for x minutes or infinite
    
    # want to clear the persistent storage
    # keep the structure intact

    print(f"Clearing file")
    set_experiment_data(data_structure)
    print("File cleared successfully.")
    
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
    
    #Get empty strucutre
    data_structure_copy = data_structure.copy()
    data_structure_copy.update({
        "TestType": meta_data['testType'],
        "Operator": meta_data['operatorName'],
        "Notes": meta_data['notes'],
        "InitialWeight": initial_weight,
        "FinalWeight": final_weight
    })
    set_experiment_data(data_structure_copy)
    
    start_reading(buffer=buffer, date_time=date_time)
        


def connect_port():
    attempt = 0
    while attempt < 5:
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
            print(f"Successfully connected to port")
            return serialPort
        except serial.SerialException as e:
            print(f"Attempt {attempt + 1}/5 failed: {e}")
            attempt += 1
            time.sleep(2 ** attempt)
    
    print(f"Failed to connect to after 5 attempts.")
    return None

def start_reading(buffer, date_time):
    global is_reading_active
    print("in the function start reading")
    print(buffer)
    
    end_time = None
    serialPort = connect_port()  # Initial connection
    
    if serialPort:
        try:
            serialPort.reset_input_buffer()  # Clear buffer
            is_reading_active = True
            
            while end_time is None:
                if stop_flag.is_set():  # Check if stop flag is set
                    print("Timer stopped")
                    break
                
                try:
                    # Check for incoming data
                    if serialPort.in_waiting > 0:
                        serialString = serialPort.readline()
                        certiString = serialString.decode()
                        print(certiString, end="")
                        
                        if date_time:  # Append date-time
                            current_time = datetime.datetime.now()
                            date_string = current_time.strftime(" %m %d %Y %H %M %S")
                            data_row = certiString[:-2] + date_string
                        else:
                            data_row = certiString[:-2]
                                        
                        buffer["Data"].append(data_row)
                        
                        # Update persistent storage
                        
                        with lock:
                            with open(FILE_PATH, 'r') as file:
                                data = json.load(file)
                            
                            data["Data"].append(data_row)
                            
                            with open(FILE_PATH, 'w') as file:
                                json.dump(data, file, indent=4)
 
                    
                    time.sleep(1)
                
                except serial.SerialException as e:
                    print(f"Connection lost with the serial port: {e}")
                    serialPort.close()
                    
                    # Attempt to reconnect
                    print("Attempting to reconnect...")
                    serialPort = connect_port()
                    
                    if not serialPort:
                        print("Reconnection failed. Exiting reading loop.")
                        break  # Exit loop if reconnection fails
                
                except Exception as e:
                    print(f"Unexpected error while reading: {e}")
        
        finally:
            # Ensure the serial port is closed
            if serialPort and serialPort.is_open:
                serialPort.close()
                print("Serial port closed.")
            
            is_reading_active = False
    
    else:
        print("Failed to connect to the serial port. Cannot start reading.")
    
    print("Timer completed")
    print(buffer)



def end_reading():
    global stop_flag
    global is_reading_active
    #is_reading_active = False
    
    #Fetch from the redis
    with lock:
        with open(FILE_PATH, 'r') as file:
            redis_data = json.load(file)

    stop_flag.set() 
    
    return redis_data

def read_live_data_from_persistent_storage():
    with lock:
        with open(FILE_PATH, 'r') as file:
            redis_data = json.load(file)

    return redis_data["Data"]
        