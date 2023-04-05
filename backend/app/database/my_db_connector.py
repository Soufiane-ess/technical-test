import logging
import sqlite3
from app.backendutils.backend_utils import PathValidator
from sqlite3 import Error

logger = logging.getLogger("odds-calculator")


class MyDbManager:

    def __init__(self, db_path: str) -> None:
        self.database_path = db_path
        # validate DB path
        if not PathValidator.is_db_path_valid(db_path):
            logging.error('Database path validation error. Check the provided path: %s', db_path)
            raise ValueError('Database path validation error.')

        self.connection = sqlite3.connect(self.database_path)
        logging.debug('successfully connected to path: %s', self.database_path)
        self.cursor = self.connection.cursor()

    def read_DB_routes_table(self):
        """ read SQLite database ROUTES table and returns its content """

        res = []
        try:
            res = self.cursor.execute("SELECT * FROM ROUTES")
        except Error as e:
            logging.error(e)
            return []

        return res.fetchall()

    def close_DB_connection(self):
        if self.connection:
            self.connection.close()
