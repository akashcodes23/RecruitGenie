import psycopg2
import psycopg2.extras
import os

class PostgresHandler:
    def __init__(self):
        self.connection = psycopg2.connect(os.getenv('POSTGRES_URL'))

    def execute_query(self, query, params=None):
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return None

    def close(self):
        self.connection.close()

