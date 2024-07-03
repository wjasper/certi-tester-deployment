import mysql.connector
from app import HOST, USER, PASSWORD, DATABASE


# Define your database configuration
DB_CONFIG = {
    'host': HOST,
    'user': USER,
    'password': PASSWORD,
    'database': DATABASE
}

def initialize_database():
    """
    First initalises a connection with mysql,
    And then runs the .sql file, which creates db and tables
    """   
    DB_CONFIG['database'] = None
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Run the SQL script
    with open('certi_tester_db_schema.sql', 'r') as file:
        sql_commands = file.read()

    for command in sql_commands.split(';'):
        cursor.execute(command + ";")

    connection.commit()
    connection.close()


def create_pool():
    global pool
    """
    try to create a pool,
    if failed then we initilze the database
    after then we again call create_pool, 
    which should be succesfull and the return the pool
    """
    try:
        # Create a connection pool
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=10,  
            **DB_CONFIG
        )
        return pool
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            initialize_database()
            return create_pool()  
        else:
            raise err

pool = None
if pool is None:
    create_pool()
        
def start_connection():
    """
    Establishes connection with mysql server, optionally specifying a database.
    """
    
    global pool
    
    #Just for safety
    if pool is None:
        create_pool()
        
    connection = pool.get_connection()
    return connection

def end_connection(connection):
    """
    Ends the connection with mysql server
    """
    connection.close()

         
def verify_database_connection():
    """
    Checks if the "certi_tsi" database exists after establishing connection.
    If it exists, returns True.
    If it doesn't exist, returns False.
    Ensures any open connections are closed.
    """
    connection = None
    try:
        connection = start_connection()
        if connection.is_connected():
            return True
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_BAD_DB_ERROR:
            return False
        raise e  # Re-raise unexpected errors
    finally:
        if connection is not None:
            end_connection(connection)