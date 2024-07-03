import database_management
import pandas as pd
from decimal import Decimal

def analyze_test_records():
    query = """SELECT * FROM test_record"""
    connection =  database_management.start_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    database_management.end_connection(connection)
    
    columns = ["Sample Tag", "Test Type", "Operator", "Comment"]
    df = pd.DataFrame(results, columns=columns)
    
    return df.to_dict(orient='records')

def analyze_penetration_data(table, sample_tag=None):
    """"
    If sample tag is None, selects all the data from Penetration Table,
    and groups by the sampleTag because we want to see the data statistics group wise.
    """
    query = """
        SELECT 
            sample_tag, 
            ROUND(AVG(penetration), 3) AS mean_penetration,
            ROUND(MAX(penetration), 3) AS max_penetration,
            ROUND(MIN(penetration), 3) AS min_penetration,
            ROUND(STDDEV(penetration), 3) AS std_dev_penetration,
            ROUND(VAR_SAMP(penetration), 3) AS variance_samp_penetration,
            ROUND(TIMESTAMPDIFF(SECOND, MIN(test_time), MAX(test_time)) / 60, 3) AS time_difference_in_minutes
        FROM
    """
    
    query += table
    
    if sample_tag is not None:
        query += " WHERE sample_tag = %s"
        params = (sample_tag,)
    else:
        params = None
        query += " GROUP BY sample_tag"
    
    connection =  database_management.start_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    database_management.end_connection(connection)
    
    columns = ["Sample Tag", "Mean Penetration", "Max Penetration", "Min Penetration", 
               "Standard Deviation", "Sample Variance", 
               "Time Difference (Minutes)"]
    
    df = pd.DataFrame(results, columns=columns)
    return df.to_dict(orient='records')
def analyze_current_penetration_data(meta_data, sample_tag):
    """
    Analyzes the current penetration data
    """
    if meta_data[0] == "P":
        table = "penetration_test"
    elif meta_data[0] == "L":
        table = "loading_test"
    elif meta_data[0] == "G":
        table = "gravimetric_test"
 
    return analyze_penetration_data(table, sample_tag)
 
# gets the test files of types penetration which could be selected
def get_penetration_test_options():
    query = """
        SELECT sample_tag FROM test_record where test_type = 'P'
    """
    
    connection =  database_management.start_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    database_management.end_connection(connection)
    if len(results) > 0:
        results.sort()
    return results

def get_penetration_data_for_selected_files(files_array):
    all_penetration_data = []
    
    # Check if the files_array is not empty
    if not files_array:
        print("No files to process.")
        return all_penetration_data

    # Use parameterized queries to avoid SQL injection and formatting issues
    query = "SELECT penetration FROM penetration_test WHERE sample_tag = %s"

    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    for sample_tag in files_array:
        cursor.execute(query, (sample_tag,))
        results = cursor.fetchall()
        penetration_data = [result[0] for result in results]
        all_penetration_data.append(penetration_data)
    
    database_management.end_connection(connection)
    
    return all_penetration_data

def analyze_test_record(test_type, test_arrays):
    all_test_data = {}
    penetration_data = []
    resistance_data = []
    sample_tags = []
    test_time = []
    
    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    
    if test_type == "P":
        query = "SELECT penetration, resistance FROM penetration_test WHERE sample_tag = %s"
        for test in test_arrays:
            cursor.execute(query, (test,))
            results = cursor.fetchall()
            p_data = [result[0] for result in results]
            r_data = [result[1] for result in results]
            penetration_data.append(p_data)
            resistance_data.append(r_data)
            sample_tags.append(test)
    
    elif test_type == "G":
        query = "SELECT resistance, time_elapsed FROM gravimetric_test WHERE sample_tag = %s"
        for test in test_arrays:
            cursor.execute(query, (test,))
            results = cursor.fetchall()
            r_data = [result[0] for result in results]
            t_data = [float(result[1]) for result in results] 
            resistance_data.append(r_data)
            test_time.append(t_data)
            sample_tags.append(test)
    
    elif test_type == "L":
        query = "SELECT penetration, resistance, time_elapsed FROM loading_test WHERE sample_tag = %s"
        for test in test_arrays:
            cursor.execute(query, (test,))
            results = cursor.fetchall()
            p_data = [result[0] for result in results]
            r_data = [result[1] for result in results]
            t_data = [float(result[2]) for result in results] 
            penetration_data.append(p_data)
            resistance_data.append(r_data)
            test_time.append(t_data)
            sample_tags.append(test)
    
    database_management.end_connection(connection)
    
    all_test_data = {
        "penetration_data": penetration_data,
        "resistance_data": resistance_data,
        "sample_tags": sample_tags,
        "test_time": test_time,
    }
     
    return all_test_data