# ingest_api
accepts JSON data from sensor network

## Production

This is based on the current server config.

    ssh ubuntu@146.185.151.77

Initialization for the repository:

    cd e3e-ingest-api
    source venv/bin/activate

_Note: the rest of this section assumes that you are in the `e3e-ingest-api` directory._

The `source` command references an environment that is specific to this project. Basically, we don't want dependency conflicts, so we namespace all of the dependent libraries on a per-codebase basis. See (the virtualenv docs)[http://docs.python-guide.org/en/latest/dev/virtualenvs/]

To run in the foreground (good for debugging)

    python api.py

to run in the background, use `nohup`

    nohup python api.py &

If you use nohup, all output will be sent to a file called nohup.out. If you would like to see the output of the api, you can tail the output file with:

    tail -f nohup.out

## Local development

If you would like to namespace your dependencies, set up virtualenv:

    virtualenv --no-site-packages venv
    source venv/bin/activate

then you can install the dependencies

    pip install -r requirements.txt

now you can run the script

    python api.py

## Code Layout

* api.py: _Modify this if you are changing the way JSON is ingested or provided. This also has the information about the endpoints_
* config.ini _You probably won't need to worry about this. This just specifies the location of the elasticsearch instance_
* requirements.txt _A list of external dependencies for the project_
* static
    - index.html _the index page that is served when you request the `/` endpoint_
    - css
        * index.css _the styles that are loaded for the index file above_
    - js
        * index.js _the javascript that is loaded for the index file above_

## API Endpoints

For more information about the API endpoints, please see `api.py`.

