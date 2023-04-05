import logging

from app.jsonparser.my_json_parser import MyJsonParser
from app.database.my_db_connector import MyDbManager

logger = logging.getLogger("odds-calculator")


class MyOddsProcessor:
    refuel_duration = 1
    refuel_label = 'Refuel'
    first_mission_day = 0
    day_waiting_to_avoid_bh = 1

    def __init__(self, mf_json_path: str, bounty_hunters_plans_path: str) -> None:

        # 1. load millennium-falcon.json
        mf_config: dict = MyJsonParser.parse_json_file_from_location(mf_json_path)
        if not mf_config:
            logger.error(f'could not load millennium-falcon configuration from provided path: {mf_json_path}')
            raise ValueError('could not load millennium-falcon configuration')
        logger.info('millennium-falcon.json configuration data successfully loaded')

        # 2. load database
        routes_data: list = self.load_database(mf_config.get('routes_db'))
        if not routes_data:
            logger.error(f'could not load routes database from provided path: {mf_config.get("routes_db")}')
            raise ValueError('could not load routes database')
        logger.info('routes database successfully loaded')

        self.connections_graph = self.build_graph(routes_data)

        # now we can close the DB
        self.db_manager.close_DB_connection()

        self.full_autonomy = mf_config.get('autonomy')
        self.origin = mf_config.get('departure')
        self.destination = mf_config.get('arrival')

        empire_plans = MyJsonParser.parse_json_file_from_location(bounty_hunters_plans_path)
        if not empire_plans:
            logger.error(f'could not load empire plans from provided path: {bounty_hunters_plans_path}')
            raise ValueError('could not load empire plans from the provided file')
        logger.info('empire.json configuration data successfully loaded')
        self.countdown = empire_plans.get('countdown')
        self.bounty_hunters_plans = empire_plans.get('bounty_hunters')

    def load_database(self, database_path: str) -> list:
        try:
            self.db_manager = MyDbManager(database_path)
        except Exception:
            # Try with path relative to configuration-files folder, where millennium-falcon.json is
            try:
                self.db_manager = MyDbManager(f"./configuration-files/{database_path}")
            except Exception:
                logger.error(
                    'Routes database could not be loaded. Please check the path provided in millennium-falcon configuration file.')
                return []

        logger.debug('routes data successfully loaded from provided DB')
        routes = self.db_manager.read_DB_routes_table()

        return routes

    def build_graph(self, db_result_set: list) -> dict:
        graph = {}
        for origin, destination, time in db_result_set:
            if origin not in graph:
                graph[origin] = {}
            graph[origin].update({destination: time})
            if destination not in graph:
                graph[destination] = {}
            graph[destination].update({origin: time})
        logger.debug('connections graph successfully built')
        return graph

    def is_bounty_hunter_present(self, planet_to_visit: str, previsional_arrival_date: str) -> bool:
        for plan in self.bounty_hunters_plans:
            if plan.get('planet') == planet_to_visit and plan.get('day') == previsional_arrival_date:
                return True
        return False

    def find_routes_clashing_with_bounty_hunters(self, distance_graph: dict, current_city: str, end_city: str,
                                                 current_travel_time: int, current_autonomy: int, visited, route):
        if current_travel_time > self.countdown:
            return

        visited.add(current_city)
        if current_city == end_city:
            yield route, current_travel_time
        else:
            for next_city, travel_time in distance_graph[current_city].items():
                if next_city not in visited:
                    if travel_time <= current_autonomy:
                        yield from self.find_routes_clashing_with_bounty_hunters(
                            distance_graph,
                            next_city,
                            end_city,
                            current_travel_time + travel_time,
                            current_autonomy - travel_time,
                            visited,
                            route + [(next_city, travel_time)],
                        )
                    else:
                        # refuel
                        yield from self.find_routes_clashing_with_bounty_hunters(
                            distance_graph,
                            next_city,
                            end_city,
                            current_travel_time + travel_time + self.refuel_duration,
                            self.full_autonomy - travel_time,
                            visited,
                            route + [(self.refuel_label, self.refuel_duration), (next_city, travel_time)],
                        )
        visited.remove(current_city)

    def find_routes_avoiding_bounty_hunters(self, distance_graph: dict, current_city: str, end_city: str,
                                            current_travel_time: int, current_autonomy: int, visited, route):
        logger.debug(f'start find_routes_avoiding_bounty_hunters between {current_city} and {end_city}')
        if current_travel_time > self.countdown:
            logger.debug('countdown reached. Abandoning this route')
            return

        visited.add(current_city)
        if current_city == end_city:
            yield route, current_travel_time
        else:
            for next_planet, travel_time in distance_graph[current_city].items():
                logger.debug(f'continue exploring routes between {current_city} and {next_planet}')
                if next_planet not in visited:
                    if travel_time <= current_autonomy and not self.is_bounty_hunter_present(next_planet, current_travel_time + travel_time):
                        yield from self.find_routes_avoiding_bounty_hunters(
                            distance_graph,
                            next_planet,
                            end_city,
                            current_travel_time + travel_time,
                            current_autonomy - travel_time,
                            visited,
                            route + [(next_planet, travel_time)],
                        )
                    elif travel_time > current_autonomy and not self.is_bounty_hunter_present(next_planet, current_travel_time + travel_time + self.refuel_duration):#<=
                        # refuel
                        logger.debug(f'refuel than go to planet: {next_planet}')
                        yield from self.find_routes_avoiding_bounty_hunters(
                            distance_graph,
                            next_planet,
                            end_city,
                            current_travel_time + travel_time + self.refuel_duration,
                            self.full_autonomy - travel_time,
                            visited,
                            route + [(self.refuel_label, self.refuel_duration), (next_planet, travel_time)],
                        )
                    elif self.is_bounty_hunter_present(next_planet, current_travel_time + travel_time):
                        # wait for one day for bounty hunters to leave
                        logger.debug(f'waiting for {self.day_waiting_to_avoid_bh} day(s) for bounty hunters to leave {next_planet}')
                        yield from self.find_routes_avoiding_bounty_hunters(
                            distance_graph,
                            current_city,
                            end_city,
                            current_travel_time + self.day_waiting_to_avoid_bh,
                            current_autonomy,
                            visited,
                            route + [('wait', self.day_waiting_to_avoid_bh)],
                        )
        if current_city in visited:
            visited.remove(current_city)

    def find_all_routes_avoiding_bounty_hunters(self):
        logger.info(f'start find_routes_avoiding_bounty_hunters between {self.origin} and {self.destination}')
        all_routes = list(self.find_routes_avoiding_bounty_hunters(
            self.connections_graph, self.origin, self.destination,
            self.first_mission_day, self.full_autonomy, set(),
            [(self.origin, 0)])
        )
        logger.info(f'{len(all_routes)} routes avoiding bounty hunters to Endor found')
        return all_routes

    def find_all_routes_crossing_bounty_hunters(self):
        logger.info('no routes avoiding bounty hunters, no escape from clash')
        logger.info(f'start find_routes_clashing_with_bounty_hunters between {self.origin} and {self.destination}')
        all_routes = list(self.find_routes_clashing_with_bounty_hunters(
            self.connections_graph, self.origin, self.destination,
            self.first_mission_day, self.full_autonomy,
            set(), [(self.origin, 0)])
        )
        logger.info(f'{len(all_routes)} routes crossing bounty hunters to Endor found')
        return all_routes

    def compute_routes_odds(self, routes_with_bounty_hunters: list) -> list:
        def is_there_bounty_hunters(stop_over: str, date_at_stop: int) -> bool:
            for plan in self.bounty_hunters_plans:
                if plan.get('planet') == stop_over and plan.get('day') == date_at_stop:
                    return True
            return False

        def is_refuel_planet(planet_name: str) -> bool:
            return self.refuel_label == planet_name

        def compute_capture_proba(encountred_bh: int) -> float:
            def my_function(k: int):
                return (9 ** k) / (10 ** (k + 1))

            proba: float = 0.1
            for i in range(1, encountred_bh):
                proba += my_function(i)
            return proba

        def compute_route_odds(route_with_stops: list) -> float:
            cumulated_travel_duration: int = 0
            encountred_bh_count: int = 0
            for idx, route_stop in enumerate(route_with_stops):
                current_planet: str = route_stop[0]
                if idx == (len(route_with_stops) - 1):
                    cumulated_travel_duration += route_stop[1]
                    continue
                if self.refuel_label == current_planet:
                    continue

                cumulated_travel_duration += route_stop[1]
                if is_there_bounty_hunters(current_planet, cumulated_travel_duration):
                    encountred_bh_count += 1
                    if is_refuel_planet(route_with_stops[idx + 1][0]):
                        cumulated_travel_duration += self.refuel_duration
                        encountred_bh_count += 1
            assert encountred_bh_count > 0
            return compute_capture_proba(encountred_bh_count)

        routes_with_odds: list = []
        for route in routes_with_bounty_hunters:
            route_odds = compute_route_odds(route[0])
            routes_with_odds.append(route + (1 - route_odds,))

        return routes_with_odds
