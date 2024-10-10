import os

# MySQL credentials
if os.getenv('RUNNING_IN_DOCKER'):
    HOST = 'mysql'
else:
    HOST = 'localhost'

USER = 'root'
PASSWORD = 'root'
DATABASE = 'certi_tsi'