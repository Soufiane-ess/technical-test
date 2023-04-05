import json
import logging

from app.backendutils.backend_utils import PathValidator

logger = logging.getLogger("odds-calculator")


class MyJsonParser:

    @staticmethod
    def parse_json_file_from_location(file_path: str) -> dict:
        res: dict = {}
        logging.debug('Start parsing json file')
        # 1. validate provided path
        if PathValidator.is_json_file_path_valid(file_path):
            logging.debug('provided json file path is valid : %s', file_path)
            # 2. read json file
            with open(file_path, 'r') as json_file:
                try:
                    res = json.load(json_file)
                    logging.debug('json file successfully parsed')
                except Exception:
                    logging.error('The provided JSON is invalid')
        else:
            logging.error('provided json file path is invalid: %s', file_path)

        return res
