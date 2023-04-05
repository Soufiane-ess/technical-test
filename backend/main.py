import logging
import json

from flask import Flask, request
from waitress import serve
from app.oddsprocessor.my_odds_processor import MyOddsProcessor
from app.backendutils.backend_utils import PathValidator

app = Flask(__name__)

logger = logging.getLogger("odds-calculator")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(
    filename='./logs/backend.log',
    encoding='utf-8'
)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

default_mf_json_path = f'./configuration-files/millennium-falcon-1.json'
default_empire_json_path = f'./configuration-files/empire_1.json'


def convert_routes_list_to_json(routes: list, with_odds: bool) -> str:
    json_list = []

    for item in routes:
        json_dict = {"route": dict(item[0]), "duration": item[1]}
        if with_odds:
            json_dict["odds"] = "{0:.0%}".format(item[2])
        else:
            json_dict["odds"] = "100%"
        json_list.append(json_dict)

    return json.dumps(json_list)


def generate_formatted_odds(mf_json_path: str, bh_plans_path: str):
    try:
        odds_processor = MyOddsProcessor(mf_json_path, bh_plans_path)
    except ValueError as ve:
        return '{"message": "' + ve.args[0] + '"}', 400

    # find routes
    routes_avoiding_bounty_hunters: list = odds_processor.find_all_routes_avoiding_bounty_hunters()
    if routes_avoiding_bounty_hunters:
        # return routes with success rate 100%
        return convert_routes_list_to_json(routes_avoiding_bounty_hunters, False)
    else:
        routes_crossing_bounty_hunters: list = odds_processor.find_all_routes_crossing_bounty_hunters()
        if routes_crossing_bounty_hunters:
            # compute odds
            routes_with_odds: list = odds_processor.compute_routes_odds(routes_crossing_bounty_hunters)
            return convert_routes_list_to_json(routes_with_odds, True)
        else:
            return '[{"route": {}, "duration":0, "odds": "0%"}]'


@app.route('/config-files-path', methods=['GET'])
def config_files_path():
    mf_json_path: str = request.args.get('falcon')
    empire_json_path: str = request.args.get('empire')
    logger.info(f'config-files-path request - received params : falcon={mf_json_path}, empire={empire_json_path}')
    message: str = ''

    if not PathValidator.is_json_file_path_valid(mf_json_path):
        logger.error('config-files-path request - path received for millennium-falcon.json invalid')
        message = f'the provided path for millenium-falcon.json: {mf_json_path} is invalid'

    if not PathValidator.is_json_file_path_valid(empire_json_path):
        logger.error('config-files-path request - path received for empire.json invalid')
        message += f'the provided path for empire.json: {empire_json_path} is invalid'

    if message:
        return '{"message": "{' + message + '}"}', 400

    return generate_formatted_odds(mf_json_path, empire_json_path)


@app.route('/upload', methods=['POST'])
def upload_plans():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            empire_file_path: str = f'./configuration-files/{file.filename}'
            file.save(empire_file_path)
            logger.info(f'upload-plans request - empire plans file successfully uploaded: {empire_file_path}')
            return generate_formatted_odds(default_mf_json_path, empire_file_path)
        else:
            return '{"message": "no file provided"}', 400
    else:
        return '{"message": "GET method not allowed for upload"}', 400


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
