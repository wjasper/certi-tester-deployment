import database_management
import pandas as pd
from datetime import datetime
import mysql.connector

def sample_tag_generator(df, filename):
    """"
    SampleTag is generated using combination of:
    Name of the file  + Unix of timestamp of the first record in the file
    """
    
    filename_without_extension = filename.replace(".txt", "")
    
    timestamp = df.iloc[0]['Timestamp']
    unix_timestamp = str(timestamp.timestamp())
    
    sample_tag = filename_without_extension.replace(" ", "") + "_" + unix_timestamp
    
    return sample_tag


def insert_g_data(df, sample_tag):
    connection = database_management.start_connection()
    cursor = connection.cursor()
   
    sql_query = """
        INSERT INTO gravimetric_test (
            sample_tag, flow_rate, photometer_reading, resistance, concentration, time_elapsed, weight_difference, test_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Add sample_tag to the beginning of each row's values
    values = df.to_numpy().tolist()
    values = [[sample_tag] + row for row in values]
    
    cursor.executemany(sql_query, values)
    
    connection.commit()
    cursor.close()

    database_management.end_connection(connection)

    return


def insert_load_data(df, sample_tag):
    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    sql_query = """
        INSERT INTO loading_test (
            sample_tag, flow_rate, penetration, photometer_reading, mass_challenged_filter, resistance, test_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    # Add sample_tag to the beginning of each row's values
    values = df.to_numpy().tolist()
    values = [[sample_tag] + row for row in values]
    
    cursor.executemany(sql_query, values)
    
    connection.commit()
    cursor.close()

    database_management.end_connection(connection)

    return


def insert_penetration_data(df, sample_tag):
    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    sql_query = """
        INSERT INTO penetration_test (
            sample_tag, flow_rate, resistance, photometer_reading, penetration, test_time
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # Add sample_tag to the beginning of each row's values
    values = df.to_numpy().tolist()
    values = [[sample_tag] + row for row in values]
    
    cursor.executemany(sql_query, values)
    
    connection.commit()
    cursor.close()

    database_management.end_connection(connection)

    return


def insert_test_record(meta_data, df, filename):
    
    #try to insert into test record if that is successful
    #then try to insert into individual table
    
    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    try:
        test_type = meta_data[0].strip('"') 
        operator = meta_data[1].strip('"') 
        comment = meta_data[2].strip('"') 
    except IndexError:
        test_type = operator = comment = None
    
    sample_tag = sample_tag_generator(df, filename)
    
    query = "INSERT INTO test_record (sample_tag, test_type, operator, comment) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (sample_tag, test_type, operator, comment))
        connection.commit()
        
        if meta_data[0] == "G":
            insert_g_data(df,sample_tag)
        elif meta_data[0] == "P":
            insert_penetration_data(df,sample_tag)
        elif meta_data[0] == "L":
            insert_load_data(df,sample_tag)
        
    except mysql.connector.IntegrityError as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        database_management.end_connection(connection)
        
    return