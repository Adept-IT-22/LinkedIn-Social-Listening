#This module will handle all database operations
import psycopg
import logging
from config import Config

#create connection to database
def db_connection():
    return psycopg.connect(
        host = Config.DB_HOST,
        name = Config.DB_NAME,
        port = Config.DB_PORT,
        user = Config.DB_USER,
        password = Config.DB_PASSWORD,
    )

#save company in database
def insert_company(name, industry, location, employee_count):
    try:
        with db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO companies (name, industry, location, employee_count) VALUES (%s, %s, %s, %s) RETURNING company_id",
                    (name, industry, location, employee_count)
                )
                #fetch company id to use as foreign key in authors table
                company_id = cur.fetchone()[0]

                #commit and return company id
                conn.commit()
                return company_id
    #log error
    except Exception as e:
        logging.error("Error: ", e)

#save author in database
def insert_author(name, title, company_id):
    try:
        with db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO authors (name, title, company_id) VALUES (%s, %s, %s)",
                    (name, title, company_id)
                )
            conn.commit()
    #log error
    except Exception as e:
        logging.error("Error: ", e)