import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database_management module from the parent directory
import database_management



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
