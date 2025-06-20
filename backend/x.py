import psycopg2
from urllib.parse import urlparse

db_url = urlparse(DB_URL)
print(f"Attempting connection to: {db_url.hostname}:{db_url.port}")

try:
        conn = psycopg2.connect(
                        host=db_url.hostname,
                                port=db_url.port,
                                        user=db_url.username,
                                                password=db_url.password,
                                                        database=db_url.path[1:]
                                                            )
            print("Connection successful!")
except Exception as e:
        print(f"Connection failed: {str(e)}")
