#!/usr/bin/env python3

import requests
import argparse
import json

parser = argparse.ArgumentParser(description='CLI program that takes millennium-falcon.json and empire.json files'
                                             ' paths as input, and prints the highest probability of success'
                                             ' as a number ranging from 0 to 100')
parser.add_argument('mf_path', help='millennium-falcon.json file path')
parser.add_argument('em_path', help='empire.json file path')
args = parser.parse_args()

url = 'http://127.0.0.1:8080/config-files-path'

response = requests.get(url, params={'falcon': args.mf_path, 'empire': args.em_path},
                        headers={"content-type": "application/json"})

if response.status_code == requests.codes.ok:
    possible_routes = json.loads(response.text)
    sorted_possible_routes = sorted(possible_routes, key=lambda possible_route: int(possible_route.get('odds')[:-1]), reverse=True)
    print(sorted_possible_routes[0].get('odds'))
else:
    print('Error: {}, status: {}'.format(response.text, response.status_code))
