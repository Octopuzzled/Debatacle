import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")

connection = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    database="debatacle"
)
