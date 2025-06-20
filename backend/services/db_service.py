#This module contains all database operations

import psycopg
import logging
from datetime import date
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

#Fetch data from database for download excel function
def fetch_data_for_download_excel(target_date: date = None) -> list:
    leads_data = []
    try:
        logger.info("Fetching today's leads for excel file...")
        if target_date is None:
            target_date = date.today()

        with psycopg.connect(conninfo = DB_URL) as conn:
            with conn.cursor() as cur:
                sql_query = """
                SELECT 
                    p.post_id,
                    p.author_id,
                    p.linkedin_post AS linkedin_post, 
                    a.name AS author_name,
                    a.title, 
                    a.company_id,
                    a.score,
                    c.name AS company_name,
                    c.location,
                    c.employee_count,
                    c.industry, 
                FROM
                    posts AS p
                JOIN 
                    authors AS a on p.author_id = a.author_id
                LEFT JOIN
                    companies AS c on a.company_id = c.company_id
                WHERE
                    DATE(p.created_at) = %s
                ORDER BY
                    p.created_at DESC
                """
                cur.execute(sql_query, (target_date,))

                leads_data = cur.fetchall()

                logger.info("Data fetched for excel file")

    except Exception as e:
        logger.error(f"Failed to fetch data from database: {str(e)}", exc_info=True)
        raise

    return leads_data       
