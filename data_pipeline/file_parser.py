import pandas as pd
import json

def parse_penetration_data(data):
    parsed_data = []
    
    for entry in data:
        parts = entry.strip().split()
        flow_rate = resistance = penetration = None
        year = month = day = hour = minute = second = None
        # Because this can be missing
        photo_reading = 0
        skip_entry = False

        try:
            # Parse flow rate, resistance, photo reading, and penetration
            for i in range(len(parts) - 1):
                if parts[i] == 'F':
                    flow_rate = float(parts[i + 1])
                elif parts[i] == 'R':
                    resistance = float(parts[i + 1])
                elif parts[i] == 'U':
                    photo_reading = float(parts[i + 1])
                elif parts[i] == 'P':
                    penetration = float(parts[i + 1])
                    # Skip entry if penetration is invalid
                    if penetration < 0 or penetration > 100:
                        skip_entry = True
                        break
    
            # Parse timestamp
            month = int(parts[-6])
            day = int(parts[-5])
            year = int(parts[-4])
            hour = int(parts[-3])
            minute = int(parts[-2])
            second = int(parts[-1])
        
            print([year, month, day, hour, minute, second])
            print([flow_rate, resistance, penetration])

        except (ValueError, IndexError):
            # Skip entry if there is a conversion error or missing data
            continue
        
        
        if skip_entry or None in [year, month, day, hour, minute, second] or None in [flow_rate, resistance, penetration]:
            continue 
        
        # Construct the timestamp
        timestamp = pd.to_datetime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
        
        # Append the parsed data (flow_rate, resistance, photo_reading, penetration, and timestamp parts)
        parsed_data.append([flow_rate, resistance, photo_reading, penetration, timestamp])
        
    return parsed_data


def parse_load_data(data):
    parsed_data = []
    
    for entry in data:
        parts = entry.strip().split()
        flow_rate = resistance = photo_reading = penetration = mass_challenged_filter = None
        year = month = day = hour = minute = second = None
        skip_entry = False 
        
        try:
            for i in range(len(parts) - 1):
                if parts[i] == 'F':
                    flow_rate = float(parts[i + 1])
                elif parts[i] == 'R':
                    resistance = float(parts[i + 1])
                elif parts[i] == 'U':
                    photo_reading = float(parts[i + 1])
                elif parts[i] == 'P':
                    penetration = float(parts[i + 1])
                    if penetration > 100 or penetration < 0:  # Invalid penetration, skip entry
                        skip_entry = True
                        break
                elif parts[i] == 'M':
                    mass_challenged_filter = float(parts[i + 1])
                elif parts[i] == 'mv':
                    month = int(parts[i+1])
                    day = int(parts[i+2])
                    year = 2000 + int(parts[i+3])
                    hour = int(parts[i+4])
                    minute = int(parts[i+5])
                    second = int(parts[i+6])
        except (ValueError, IndexError):
            # Skip the entry if there is a conversion error
            continue
        
        # Skip the entry if any required values are missing or penetration is invalid
        if skip_entry or None in [year, month, day, hour, minute, second] or None in [flow_rate, resistance, photo_reading, penetration, mass_challenged_filter]:
            continue 
        
        # Construct the timestamp
        timestamp = pd.to_datetime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
        
        # Append the parsed data
        parsed_data.append([flow_rate, resistance, photo_reading, penetration, mass_challenged_filter, timestamp])

    return parsed_data


def parse_g_data(data, weight_delta):
    parsed_data = []
    
    for entry in data:
        parts = entry.strip().split()
        flow_rate = resistance = photo_reading = concentration = minutes_passed = None
        year = month = day = hour = minute = second = None
        skip_entry = False
        
        try:
            for i in range(len(parts) - 1):
                if parts[i] == 'F':
                    flow_rate = float(parts[i + 1])
                elif parts[i] == 'R':
                    resistance = float(parts[i + 1])
                elif parts[i] == 'U':
                    photo_reading = float(parts[i + 1])
                elif parts[i] == 'c':
                    concentration = float(parts[i + 1])
                    # Skip entry if concentration is outside valid range (0-100)
                    #if concentration < 0 or concentration > 100:
                     #   skip_entry = True
                      #  break
                elif parts[i] == 'mg/m3':
                    month = int(parts[i + 1])
                    day = int(parts[i + 2])
                    year = 2000 + int(parts[i + 3])
                    hour = int(parts[i + 4])
                    minute = int(parts[i + 5])
                    second = int(parts[i + 6])
                elif parts[i] == 'T':
                    minutes_passed = float(parts[i + 1])
        except (ValueError, IndexError):
            # Skip entry if there is a conversion error or missing data
            continue
        
        # Ensure timestamp information is complete and valid
        if skip_entry or None in [year, month, day, hour, minute, second] or  None in [flow_rate, resistance, photo_reading, concentration, minutes_passed]:
            continue
        
        # Construct the timestamp
        timestamp = pd.to_datetime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
    
        # Append the parsed data (flow_rate, resistance, photo_reading, concentration, minutes_passed, weight_delta, and timestamp)
        parsed_data.append([flow_rate, resistance, photo_reading, concentration, minutes_passed, weight_delta, timestamp])
    
    return parsed_data

def process_penetration_data(data):
    df = pd.DataFrame(data, columns=['Flow Rate (liter/min)', 'Resistance (mm of H2O)', 'Photometric Reading (mV)', 'Penetration (%)', 'Timestamp'])
    return df


def process_g_data(data):
    df = pd.DataFrame(data, columns=['Flow Rate (liter/min)', 'Resistance (mm of H2O)', 'Photometric Reading (mV)', 'Concentration', 'Minutes Passed', 'Delta weight', 'Timestamp'])
    df['Minutes Passed'] = df['Minutes Passed'].round(2)
    return df

def process_load_data(data):
    df = pd.DataFrame(data, columns=['Flow Rate (liter/min)', 'Resistance (mm of H2O)', 'Photometric Reading (mV)', 'Penetration (%)', 'Mass Challenged Filter (mg)', 'Timestamp'])
    df['Minutes Passed'] = ((df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds() / 60).round(2)
    return df


def file_parse(file):
    file_content = file.read().decode('utf-8') 
    json_data = json.loads(file_content)
    
    test_type = json_data.get('TestType')
    operator = json_data.get('Operator')
    notes = json_data.get('Notes')
    data = json_data.get('Data')
    
    meta_data = {
        'test_type': test_type,
        'operator': operator,
        'notes': notes
    }
    
    # Process the data based on the TestType
    if test_type == "P":
        processed_data = parse_penetration_data(data)
        df = process_penetration_data(processed_data)
        print(df)
        return meta_data, df

    elif test_type == "L":
        processed_data = parse_load_data(data)
        df = process_load_data(processed_data)
        return meta_data, df
    
    elif test_type == "G":
        initial_weight = float(json_data.get('InitialWeight'))
        final_weight = float(json_data.get('FinalWeight'))

        # Calculate the delta weight and round it to 2 decimal places
        weight_delta = round(final_weight - initial_weight, 2)
        
        processed_data = parse_g_data(data, weight_delta)
        df = process_g_data(processed_data)
        return meta_data, df
    
    else:
        return None
       
def df_data_formatting(df):
    """
    Converts into a suitable form to be displayed in the HTML table
    """
    df_display = df.copy()
    df_display['Timestamp'] = df_display['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_display.rename(columns={'Timestamp': 'Timestamp (YYYY-MM-DD HH:MM:SS)'}, inplace=True)
    return df_display.to_dict(orient='records')