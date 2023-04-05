# Giskard technical test - Soufiane Essamadi


## Application architecture

As requisted in the exercice, the application have 3 components: back-end, front-end, and CLI.

### Back-end
It's the core of the application, as it holds the odds computing workflow, and returns the computation result to the other components.
In this implementation, the back-end is based on a web server (Flask), accepting trafic from anywhere on port __8080__, and must be the first to start.
It will then wait for requests from the other components to compute odds, according to the provided inputs.

### Front-end
A single page application based on React, connected to the Flask server, used to upload empire plans file.
The React app is to start after the back-end, and is accessible from : http://localhost:3000/.

When a file is uploaded in the React app page, the front-end will send an HTTP POST request containing the file to the back-end, which will start an odds computation process, and return the result.

### CLI
The third component of the application. When executed, the command line will take the paths of the configuration files as inputs, and send an HTTP GET request with the provided arguments as request parameters to the back-end.
The back-end will return the computation result to the CLI for display.

## Starting the app

### Starting the back-end
In the _**/odds-calculator-app/backend_ directory, __main.py__ script starts the application web server.
Before running this script, make sure you have created a virtual environment to hold project dependencies, listed in the _requirements.txt_ file.
With the virtual environment activated, to install requirements use :
```
pip install -r /path/to/requirements.txt
```
Then start the server with :
```
python main.py
```
When the server is started, it will listen on port __8080__.

### Starting the front-end
The front-end is based on React.
Make sure you have _npm_ installed (https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
Go to the the _**/odds-calculator-app/_ directory, and run :
```
npm start
```
The default react application page should pop up in your browser, if it does not, copy and open "http://localhost:3000/" in your browser.
File upload page should be displayed.

### CLI
An executable script (calculate-odds.py). Make sure to provide execution right on this script:
```
chmod +x /path/to/calculate-odds.py
```
The script can be configured to run from anywhere, by setting the used backend address in the _url_ variable in the script.
If runned from the machine hosting the backend, there's no need to change the _url_.

The first expected parameter is a path to the millennium-falcon.json on the backend server, and the second the path to empire.json on the same server.
Example command:
```
/path/to/calculate-odds.py configuration-files/example-millennium-falcon.json configuration-files/example_empire.json
```

## Tests

To run __database__ tests, go to _"**/odds-calculator-app/backend"_ and execute :
```
python -m unittest -v app.database.test_my_db_connector
```

To run __jsonparser__ unit tests, go to _"**/odds-calculator-app/backend"_ and execute :
```
python -m unittest -v app.jsonparser.test_my_json_parser
```

For __odds processor__ test, in _"**/odds-calculator-app/backend"_ execute :
```
python -m unittest app.oddsprocessor.test_my_odds_processor
```


## Utility folders
__**/odds-calculator-app/backend/configuration-files__ folder is used to store configuration files used for tests, as well as uploaded empire.json.

__**/odds-calculator-app/backend/db-files__ folder is used to store SQLite database files.

__**/odds-calculator-app/backend/logs__ folder contains the main logging file for the backend app.


Thank you