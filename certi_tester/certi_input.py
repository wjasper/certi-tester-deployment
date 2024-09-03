"""
Created on Thu Sep 21 13:52:59 2023

This program reads data from the TSI CERTITEST 8130A
and outputs the data to a file.

@author: wjasper@ncsu.edu
"""

import serial
import json
import time
import datetime
import sys
import select

serialString = ""
date_time = False


serialPort = serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=9600,
    bytesize=serial.SEVENBITS,
    timeout=2,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_ODD,
    rtscts=True,
    dsrdtr=True)


initial_weight = None
final_weight = None

test_type = input("Enter the type of test [GPL]: ").upper()
if test_type == 'G':         # gravimetric test
    initial_weight = input("Enter initial weight [mg]: ")
elif test_type == 'P':       # penetration test
    date_time = True
elif test_type == 'L':       # loading test
    pass
else:
    print("Unknown test type.")
    sys.exit(0)

operator = input("Enter operator name: ")
notes = input("Enter notes: ")
buffer = "TT " + test_type + '\nO "' + operator + '"\nT "' + notes + '"\n'  #add test type and notes
buffer2 = {"TestType": test_type, "Operator": operator, "Notes": notes,
                "InitialWeight": initial_weight, "FinalWeight": final_weight, "Data": []
                }

input("Hit Enter to continue: ")
print("Hit 's' to stop when you are done.\n")
running = True
while running:
    if sys.stdin in select.select([sys.stdin], [], [], 0) [0]:
        line = sys.stdin.readline()
        # line = sys.stdin.read(1)
        if 's' in line:
            running = False          

    # Wait until there is data waiting in the serial buffer
    if serialPort.in_waiting > 0:
        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()
        certiString = serialString.decode()
        print(certiString,end="")
        
        if date_time == True:  # append a date time
            current_time = datetime.datetime.now()
            date_string = current_time.strftime(" %m %d %Y %H %M %S")
            buffer += certiString[:-2] + date_string + '\n'
            buffer2["Data"].append(certiString[:-2] + date_string)
        else:
            buffer += certiString
            buffer2["Data"].append( certiString[:-2])

    time.sleep(1)        

if test_type == 'G':
    final_weight = input("Enter final weight [mg]: ")
    buffer += "WI " + initial_weight + " WF " + final_weight
    buffer2["InitialWeight"] = initial_weight
    buffer2["FinalWeight"] = final_weight
    
print('All done')
print(buffer2)
val = input('Save data [y/n]?: ')
if val.lower() == 'y':
    filename = input('Enter filename: ')
    if not filename.endswith(".json"):
        filename += ".json"   # make sure file is .json
    with  open(filename,"w+") as fd:
        json.dump(buffer2, fd, indent=2)