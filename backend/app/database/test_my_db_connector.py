import unittest
import sqlite3
from os import path
from app.database.my_db_connector import MyDbManager


class TestConnectDb(unittest.TestCase):

    def setUp(self) -> None:
        def create_test_DB():
            conn = sqlite3.connect(self.example_db_path)
            cur = conn.cursor()
            cur.execute("CREATE TABLE ROUTES(ORIGIN varchar(255), DESTINATION varchar(255), TRAVEL_TIME int)")
            cur.execute("INSERT INTO ROUTES VALUES ('Tatooine', 'Dagobah', 4), ('Dagobah', 'Endor', 1)")
            conn.commit()
            conn.close()

        self.example_db_path: str = './db-files/example.db'
        if not path.exists(self.example_db_path):
            create_test_DB()

    def test_read_routes_table(self):
        db_manager = MyDbManager(self.example_db_path)
        routes_list: list = db_manager.read_DB_routes_table()
        self.assertTrue(len(routes_list) > 0)
        db_manager.close_DB_connection()
