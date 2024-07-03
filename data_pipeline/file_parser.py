import pandas as pd
from io import TextIOWrapper

def parse_metadata(file):
    meta_data = []
    
    for line in file:
        if line.startswith(('TT', 'O', 'T')):
            parts = line.strip().split(' ', 1)
            meta_data.append(parts[1].strip())
        else:
            break
    
    return meta_data

def parse_penetration_data(file):
    data = []
    parsing_data = False
    
    for line in file:
        if not parsing_data and 'F' in line:
            parsing_data = True
        
        if parsing_data and line.strip() and not line.startswith('#'):
            parts = line.strip().split()
            flow_rate = resistance = photo_reading = penetration = 0
            for i in range(len(parts) - 1):
                if parts[i] == 'F':
                    flow_rate = float(parts[i + 1])
                elif parts[i] == 'R':
                    resistance = float(parts[i + 1])
                elif parts[i] == 'U':
                    photo_reading = float(parts[i + 1])
                elif parts[i] == 'P':
                    penetration = float(parts[i + 1])

            month = int(parts[-6])
            day = int(parts[-5])
            year = int(parts[-4])
            hour = int(parts[-3])
            minute = int(parts[-2])
            second = int(parts[-1])

            timestamp = pd.to_datetime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")

            data.append([flow_rate, resistance, photo_reading, penetration] + list(timestamp.timetuple())[:6])

    return data


def parse_load_data(file):
    data = []
    parsing_data = False
    
    for line in file:
        if not parsing_data and 'F' in line:
            parsing_data = True
        
        if parsing_data and line.strip() and not line.startswith('#'):
            parts = line.strip().split()
            flow_rate = resistance = photo_reading = penetration = mass_challenged_filter = 0
            for i in range(len(parts) - 1):
                if parts[i] == 'F':
                    flow_rate = float(parts[i + 1])
                elif parts[i] == 'R':
                    resistance = float(parts[i + 1])
                elif parts[i] == 'U':
                    photo_reading = float(parts[i + 1])
                elif parts[i] == 'P':
                    penetration = float(parts[i + 1])
                elif parts[i] == 'M':
                    mass_challenged_filter = float(parts[i + 1])
                elif parts[i] == 'mv':
                    month = int(parts[i+1])
                    day = int(parts[i+2])
                    year = 2000 + int(parts[i+3])
                    hour = int(parts[i+4])
                    minute = int(parts[i+5])
                    second = int(parts[i+6])
            
            timestamp = pd.to_datetime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
            
            data.append([flow_rate, resistance, photo_reading, penetration, mass_challenged_filter, timestamp])

    return data

def find_delta_weight(file): 
    wi = 0
    wf = 0   
    file.seek(0)
    for line in file:
        if line.startswith('WI'):
            parts = line.split()
            wi = float(parts[1])
            wf = float(parts[3]) if len(parts) > 3 and parts[2] == 'WF' else None
            break

    return round(wf - wi, 2)


def parse_g_data(file):
    weight_delta = find_delta_weight(file)
    data = []
    parsing_data = False
    
    file.seek(0)
    for line in file:
        if not parsing_data and 'F' in line:
            parsing_data = True
        
        if parsing_data and line.strip() and not line.startswith('#'):
            parts = line.strip().split()
            flow_rate = resistance = photo_reading = concentration = minutes_passed = 0
            for i in range(len(parts) - 1):
                if parts[i] == 'F':
                    flow_rate = float(parts[i + 1])
                elif parts[i] == 'R':
                    resistance = float(parts[i + 1])
                elif parts[i] == 'U':
                    photo_reading = float(parts[i + 1])
                elif parts[i] == 'c':
                    concentration = float(parts[i + 1])
                elif parts[i] == 'mg/m3':
                    month = int(parts[i+1])
                    day = int(parts[i+2])
                    year = 2000 + int(parts[i+3])
                    hour = int(parts[i+4])
                    minute = int(parts[i+5])
                    second = int(parts[i+6])
                elif parts[i] == 'T':
                    minutes_passed = float(parts[i + 1])

                
            timestamp = pd.to_datetime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
            
            data.append([flow_rate, resistance, photo_reading, concentration, minutes_passed, weight_delta,timestamp])

    return data

def process_penetration_data(data):
    df = pd.DataFrame(data, columns=['Flow Rate (liter/min)', 'Resistance (mm of H2O)', 'Photometric Reading (mV)', 'Penetration (%)', 'year', 'month', 'day', 'hour', 'min', 'sec'])

    df[['year', 'month', 'day', 'hour', 'min', 'sec']] = df[['year', 'month', 'day', 'hour', 'min', 'sec']].astype(int)

    df['Timestamp'] = df.apply(lambda row: f"{int(row['year']):04d}-{int(row['month']):02d}-{int(row['day']):02d} {int(row['hour']):02d}:{int(row['min']):02d}:{int(row['sec']):02d}", axis=1)
    df.drop(columns=['year', 'month', 'day', 'hour', 'min', 'sec'], inplace=True)

    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    return df

def process_g_data(data):
    df = pd.DataFrame(data, columns=['Flow Rate (liter/min)', 'Resistance (mm of H2O)', 'Photometric Reading (mV)', 'Concentration', 'Minutes Passed', 'Delta weight', 'Timestamp'])
    df['Minutes Passed'] = df['Minutes Passed'].round(2)
    df.drop(df.tail(1).index, inplace=True)
    return df

def process_load_data(data):
    df = pd.DataFrame(data, columns=['Flow Rate (liter/min)', 'Resistance (mm of H2O)', 'Photometric Reading (mV)', 'Penetration (%)', 'Mass Challenged Filter (mg)', 'Timestamp'])
    df['Minutes Passed'] = ((df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds() / 60).round(2)
    return df

def file_parse(file):
    with TextIOWrapper(file, encoding='utf-8') as f:
        meta_data = parse_metadata(f)
        if meta_data[0] == "P":
            f.seek(0)
            data = parse_penetration_data(f)
            df = process_penetration_data(data)
            return meta_data, df

        elif meta_data[0] == "L":
            f.seek(0)
            data = parse_load_data(f)
            df = process_load_data(data)
            return meta_data, df
        
        elif meta_data[0] == "G":
            f.seek(0)
            data = parse_g_data(f)
            df = process_g_data(data)
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