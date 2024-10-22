import pymongo
import mysql.connector
from config import Config

# MongoDB connection
mongo_client = pymongo.MongoClient(Config.MONGO_URI)
mongo_db = mongo_client['sms_management']

# MySQL connection
mysql_db = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB
)

mysql_cursor = mysql_db.cursor()

# Example query to retrieve SMS metrics from MySQL
def get_sms_metrics():
    mysql_cursor.execute("SELECT * FROM sms_metrics")
    return mysql_cursor.fetchall()