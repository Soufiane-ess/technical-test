import unittest
import sqlite3

from os import path

from app.oddsprocessor.my_odds_processor import MyOddsProcessor
from app.database.my_db_connector import MyDbManager


class TestMyOddsProcessor(unittest.TestCase):
    def setUp(self) -> None:
        def create_test_example_db(db_name: str, data_insertion_query: str):
            conn = sqlite3.connect(f'./db-files/{db_name}')
            cur = conn.cursor()
            cur.execute("CREATE TABLE ROUTES(ORIGIN varchar(255), DESTINATION varchar(255), TRAVEL_TIME int)")
            cur.execute(data_insertion_query)
            conn.commit()
            conn.close()

        if not path.exists('./db-files/universe_1.db'):
            create_test_example_db(
                'universe_1.db',
                "INSERT INTO ROUTES VALUES ('Tatooine', 'Dagobah', 6), ('Dagobah', 'Endor', 4), "
                "('Dagobah', 'Hoth', 1), ('Hoth', 'Endor', 1), ('Tatooine', 'Hoth', 6)"
            )

        if not path.exists('./db-files/my_universe.db'):
            create_test_example_db(
                'my_universe.db',
                "INSERT INTO ROUTES VALUES ('Birren', 'Miser', 4), ('Birren', 'Corellia', 3), "
                "('Miser', 'Alderaan', 5), ('Corellia', 'Jakku', 2), ('Miser', 'Jakku', 4), ('Jakku', 'Geonosis', 2), "
                "('Miser', 'Mandalore', 3), ('Geonosis', 'Alderaan', 4)"
            )

        if not path.exists('./configuration-files/my_universe_2.db'):
            conn = sqlite3.connect(f'./configuration-files/my_universe_2.db')
            cur = conn.cursor()
            cur.execute("CREATE TABLE ROUTES(ORIGIN varchar(255), DESTINATION varchar(255), TRAVEL_TIME int)")
            cur.execute(
                "INSERT INTO ROUTES VALUES ('Birren', 'Miser', 4), ('Birren', 'Corellia', 3), "
                "('Miser', 'Alderaan', 5), ('Corellia', 'Jakku', 2), ('Miser', 'Jakku', 4), ('Jakku', 'Geonosis', 2), "
                "('Miser', 'Mandalore', 3), ('Geonosis', 'Alderaan', 4)"
            )
            conn.commit()
            conn.close()

        self.no_bh_odds_proc: MyOddsProcessor = MyOddsProcessor(
            './configuration-files/millennium-falcon.json',
            './configuration-files/empire.json'
        )
        self.bh_odds_proc: MyOddsProcessor = MyOddsProcessor(
            './configuration-files/millennium-falcon-1.json',
            './configuration-files/empire_1.json'
        )
        self.custom_odds_proc: MyOddsProcessor = MyOddsProcessor(
            './configuration-files/example-millennium-falcon.json',
            './configuration-files/example_empire.json'
        )

    def test_find_all_paths_basic(self):
        self.assertEqual(len(self.no_bh_odds_proc.find_all_routes_avoiding_bounty_hunters()), 1)

    def test_find_all_paths_example_1(self):
        self.assertEqual(len(self.bh_odds_proc.find_all_routes_avoiding_bounty_hunters()), 0)
        self.assertEqual(len(self.bh_odds_proc.find_all_routes_crossing_bounty_hunters()), 0)

    def test_find_all_paths_my_example(self):
        self.assertEqual(len(self.custom_odds_proc.find_all_routes_avoiding_bounty_hunters()), 0)
        self.assertEqual(len(self.custom_odds_proc.find_all_routes_crossing_bounty_hunters()), 1)

    def test_build_graph(self):
        db_manager = MyDbManager('./db-files/my_universe.db')
        routes_list: list = db_manager.read_DB_routes_table()
        self.assertTrue(len(routes_list) > 0)
        custom_graph = self.custom_odds_proc.build_graph(routes_list)
        self.assertTrue(len(custom_graph) > 0)
        db_manager.close_DB_connection()

    def test_find_all_paths_my_example_2(self):
        custom_odds_proc_2: MyOddsProcessor = MyOddsProcessor(
            './configuration-files/example-millennium-falcon-2.json',
            './configuration-files/example_empire_2.json'
        )
        self.assertEqual(len(custom_odds_proc_2.find_all_routes_avoiding_bounty_hunters()), 1)
