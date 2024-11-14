import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv
import os

load_dotenv()

# Load database credentials from environment variables
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST", "localhost")  # Default to localhost if not set
database = os.getenv("MYSQL_DATABASE", "debatacle")  # Default database

# Create a connection pool - this was idea auf ChatGPT, didn't have a pool before
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  # Set the number of connections in the pool
    host=host,
    user=user,
    password=password,
    database=database
)

def get_connection():
    """Get a connection from the connection pool."""
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            print("Connected to database successfully")
            return connection
    except Error as err:
        print(f"Failed to get connection from pool: {err}")
        return None

def close_connection(connection):
    """Close the database connection (returns it to the pool)."""
    if connection and connection.is_connected():
        connection.close()  # This returns the connection to the pool
        print("Database connection returned to pool.")