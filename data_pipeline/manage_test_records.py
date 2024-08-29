import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database_management module from the parent directory
import database_management
from decimal import Decimal
import datetime


def delete_test_records(test_records):

    print("hello")
    print(test_records)
    
    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    for record in test_records:
        sql_query = "DELETE FROM test_record WHERE sample_tag = %s"
        cursor.execute(sql_query, (record,))
   
    connection.commit()
    cursor.close()
    database_management.end_connection(connection)

    return

def export_test_records(test_records):
    connection = database_management.start_connection()
    cursor = connection.cursor()
    
    export_data = []

    for record in test_records:
        if record['testType'] == 'G':
            table = 'gravimetric_test'
        
        elif record['testType'] == 'L':
            table = 'loading_test'
        
        else:
            table = 'penetration_test'
        
        # Query to get all column names except 'sample_tag'
        cursor.execute(f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table}' 
              AND COLUMN_NAME NOT IN ('sample_tag', 'id')
        """)
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]

        # Construct the SELECT query with the column names
        sql_query = f"SELECT {', '.join(column_names)} FROM {table} WHERE sample_tag = %s"
        
        cursor.execute(sql_query, (record['sampleTag'],))
        result = cursor.fetchall()

        # Format datetime and Decimal objects in result
        formatted_result = []
        for row in result:
            formatted_row = []
            for item in row:
                if isinstance(item, datetime.datetime):
                    formatted_row.append(item.strftime('%Y-%m-%d %H:%M:%S'))
                elif isinstance(item, Decimal):
                    formatted_row.append(float(item))  # or use `item.quantize(Decimal('0.00'))` for fixed-point representation
                else:
                    formatted_row.append(item)
            formatted_result.append(tuple(formatted_row))

        export_data.append({
            'sampleTag': record['sampleTag'],
            'testType': record['testType'],
            'columnNames': column_names,  # Include column names in the result
            'data': formatted_result
        })
       
    connection.commit()
    cursor.close()
    database_management.end_connection(connection)
    
    return export_data
