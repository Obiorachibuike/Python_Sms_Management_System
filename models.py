import pymongo
import mysql.connector
from mysql.connector import Error
from config import Config
import logging
import time
from monitoring import log_critical_error, log_warning, log_info, log_exception

# Configure logging
# (This could be removed as logging is configured in monitoring.py)

# MongoDB connection
class MongoDB:
    def __init__(self, uri):
        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client['sms_management']
            log_info("Connected to MongoDB.")
        except Exception as e:
            log_exception(e)

    def get_collection(self, collection_name):
        try:
            return self.db[collection_name]
        except Exception as e:
            log_exception(e)
            return None


# MySQL connection with retry logic
class MySQLDatabase:
    def __init__(self, host, user, password, database, retries=3, delay=2):
        self.connection = None
        self.retries = retries
        self.delay = delay
        self.cursor = None
        self.connect(host, user, password, database)

    def connect(self, host, user, password, database):
        for attempt in range(self.retries):
            try:
                self.connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
                )
                if self.connection.is_connected():
                    self.cursor = self.connection.cursor()
                    log_info("Connected to MySQL.")
                break
            except Error as e:
                log_error = f"Error connecting to MySQL (attempt {attempt + 1}/{self.retries}): {e}"
                log_warning(log_error)
                time.sleep(self.delay)  # Wait before retrying
        else:
            log_critical_error("Failed to connect to MySQL after several attempts.")
            self.cursor = None

    def get_sms_metrics(self):
        if self.cursor is None:
            log_warning("MySQL cursor is not initialized.")
            return None
        
        try:
            query = "SELECT * FROM sms_metrics"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            log_exception(e)
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
            log_info("MySQL cursor closed.")
        if self.connection:
            self.connection.close()
            log_info("MySQL connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Initialize MongoDB and MySQL connections
mongo_db = MongoDB(Config.MONGO_URI)

# Example of using MySQLDatabase with a context manager
def fetch_sms_metrics():
    with MySQLDatabase(Config.MYSQL_HOST, Config.MYSQL_USER, Config.MYSQL_PASSWORD, Config.MYSQL_DB) as mysql_db:
        metrics = mysql_db.get_sms_metrics()
        return metrics
