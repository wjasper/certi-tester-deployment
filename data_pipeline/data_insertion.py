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

    # Map DataFrame column names to the database column names
    df_to_db_column_map = {
        'Flow Rate (liter/min)': 'flow_rate',
        'Resistance (mm of H2O)': 'resistance',
        'Photometric Reading (mV)': 'photometer_reading',
        'Concentration': 'concentration',
        'Minutes Passed': 'time_elapsed',
        'Delta weight': 'weight_difference',
        'Timestamp': 'test_time'
    }

    # Define the order of columns to insert
    db_columns = ['sample_tag'] + list(df_to_db_column_map.values())

    # Create the SQL query string
    columns_str = ', '.join(db_columns)
    placeholders_str = ', '.join(['%s'] * len(db_columns))

    sql_query = f"""
        INSERT INTO gravimetric_test (
            {columns_str}
        ) VALUES ({placeholders_str})
    """

    # Extract and map the relevant columns from the DataFrame
    values = df[list(df_to_db_column_map.keys())].to_numpy().tolist()
    values = [[sample_tag] + row for row in values]

    # Execute the SQL query
    cursor.executemany(sql_query, values)

    connection.commit()
    cursor.close()
    database_management.end_connection(connection)

    return


def insert_load_data(df, sample_tag):
    connection = database_management.start_connection()
    cursor = connection.cursor()

    print(df.columns)

    # Map DataFrame columns to the corresponding database column names
    df_to_db_column_map = {
        'Flow Rate (liter/min)': 'flow_rate',
        'Penetration (%)': 'penetration',
        'Photometric Reading (mV)': 'photometer_reading',
        'Mass Challenged Filter (mg)': 'mass_challenged_filter',
        'Resistance (mm of H2O)': 'resistance',
        'Timestamp': 'test_time',
        'Minutes Passed': 'time_elapsed'
    }

    # Define the order of columns to insert
    db_columns = ['sample_tag'] + list(df_to_db_column_map.values())

    # Create the SQL query string
    columns_str = ', '.join(db_columns)
    placeholders_str = ', '.join(['%s'] * len(db_columns))

    sql_query = f"""
        INSERT INTO loading_test (
            {columns_str}
        ) VALUES ({placeholders_str})
    """

    # Extract and map the relevant columns from the DataFrame
    values = df[list(df_to_db_column_map.keys())].to_numpy().tolist()
    values = [[sample_tag] + row for row in values]

    # Execute the SQL query
    cursor.executemany(sql_query, values)

    connection.commit()
    cursor.close()
    database_management.end_connection(connection)

    return


def insert_penetration_data(df, sample_tag):
    connection = database_management.start_connection()
    cursor = connection.cursor()
    print(df.columns)

    # Map DataFrame columns to the corresponding database column names
    df_to_db_column_map = {
        'Flow Rate (liter/min)': 'flow_rate',
        'Resistance (mm of H2O)': 'resistance',
        'Photometric Reading (mV)': 'photometer_reading',
        'Penetration (%)': 'penetration',
        'Timestamp': 'test_time'
    }

    # Define the order of columns to insert
    db_columns = ['sample_tag'] + list(df_to_db_column_map.values())

    # Create the SQL query string
    columns_str = ', '.join(db_columns)
    placeholders_str = ', '.join(['%s'] * len(db_columns))

    sql_query = f"""
        INSERT INTO penetration_test (
            {columns_str}
        ) VALUES ({placeholders_str})
    """

    # Extract and map the relevant columns from the DataFrame
    values = df[list(df_to_db_column_map.keys())].to_numpy().tolist()
    values = [[sample_tag] + row for row in values]

    # Execute the SQL query
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
    
    test_type = meta_data.get('test_type', '').strip('"')
    operator = meta_data.get('operator', '').strip('"')
    comment = meta_data.get('notes', '').strip('"')
    
    sample_tag = sample_tag_generator(df, filename)
    
    query = "INSERT INTO test_record (sample_tag, test_type, operator, comment) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (sample_tag, test_type, operator, comment))
        connection.commit()
        
        if test_type == "G":
            insert_g_data(df, sample_tag)
        elif test_type == "P":
            insert_penetration_data(df, sample_tag)
        elif test_type == "L":
            insert_load_data(df, sample_tag)
        
    except mysql.connector.IntegrityError as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        database_management.end_connection(connection)
        
    return sample_tag