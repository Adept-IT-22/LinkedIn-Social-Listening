#This module contains all database operations

import psycopg
import logging
from config.app_config import DB_CONFIG

#logger config
logger = logging.getLogger(__name__)

#Database configs
HOST = DB_CONFIG.get("host")
DB_NAME = DB_CONFIG.get("name")
PORT = DB_CONFIG.get("port")
USER_NAME = DB_CONFIG.get("user")
PASSWORD = DB_CONFIG.get("password")
DB_URL = f"postgresql://{USER_NAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

#Check if the linkedin post already exists in the DB 2 avoid duplicates
def check_if_duplicate_post_exists(linkedin_post:str) -> bool:
    try:
        logger.info("Checking for duplicate posts....")
        with psycopg.connect(conninfo = DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    #check if at least 1 duplicate exists
                    "SELECT 1 FROM authors WHERE linkedin_post = %s LIMIT 1", (linkedin_post,)
                )
                #returns true if duplicate exists, false otherwise
                return cur.fetchone() is not None
    except Exception as e:
        logger.warning("Duplicate check failed: %s", str(e))
        return False

#Insert data into author, company & post
def add_data_into_database(
        author_name: str,
        job_title: str,
        company_name: str,
        company_industry: str,
        company_location: str,
        employee_count: str,
        linkedin_post: str,
        score: int
):
    try:
        with psycopg.connect(conninfo = DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO companies (name, industry, location, employee_count) VALUES (%s, %s, %s, %s) RETURNING company_id", (company_name, company_industry, company_location, employee_count)
                )
                #fetch company id and use it in the authors table
                company_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO authors (name, title, company_id, score) VALUES (%s, %s, %s, %s) RETURNING author_id", (author_name, job_title, company_id, score)
                )
                #fetch author id and use it in posts table
                author_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO posts(author_id, linkedin_post) VALUES (%s, %s)", (author_id, linkedin_post)
                )
            conn.commit()
    except Exception as e:
        logger.warning("Saving data in DB failed: %s", str(e))
        #If the transaction has started roll it back
        if 'conn' in locals():
            try:
                conn.rollback()
            except:
                pass
        return
