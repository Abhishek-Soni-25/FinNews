import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="finnews",
        user="postgres",
        password=os.getenv("DATABASE_PASSWORD")
    )