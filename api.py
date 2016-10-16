import flask
import json
import calendar
import ConfigParser
from datetime import datetime, date, time
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

# Flask boilerplate
app = flask.Flask(__name__, static_url_path='')
app.config['DEBUG'] = True

# Configuration & elasticsearch boilerplate
parser = ConfigParser.ConfigParser()
parser.read('config.ini')
es_host = parser.get('es', 'host')
es_port = parser.get('es', 'port')

es = Elasticsearch(host=es_host, port=es_port)

# test whether json is valid
def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

# store the json in Elasticsearch. Stores the data in an index named "e3e"
def store_json(blob, index):
  try:
    print blob
    data = json.loads(blob)
    data['timestamp'] = datetime.fromtimestamp(int(data['timestamp']))
    es.index(index='e3e', doc_type=index, body=data)
    return json.dumps({'ok' : True})
  except Exception, e:
    print "unable to save in elasticsearch"
    print e
    return json.dumps({'ok' : False}, 500)

# this parses the data that is returned from Elasticsearch
def extract_data(hit):
  t = hit["_type"]
  x = hit["_source"]
  x["type"] = t
  return x

# Creates an Elasticsearch query for points within a bounding box
def build_e3e_event_query(minLat, minLon, maxLat, maxLon):
  query = {
    "query": {
      "filtered" : {
        "query" : {
          "match_all" : {}
        },
        "filter" : {
          "geo_bounding_box" : {
            "location" : {
              "bottom_left" : {
                "lat" : str(minLat),
                "lon" : str(minLon)
              },
              "top_right" : {
                "lat" : str(maxLat),
                "lon" : str(maxLon)
              }
            }
          }
        }
      }
    }
  }
  print query
  return query


# This functtion just abstracts away some of the Elasticsearch query boilerplate
def es_lookup(index, typ, query):
  res = es.search(index=index, doc_type=typ, body=query, size=400)
  hits = res["hits"]["hits"]
  rowList = []
  if len(hits) > 0:
    rowList = map(extract_data, hits)
  return rowList

# The root route. This just returns the "index.html" file
@app.route('/')
def root():
  return app.send_static_file('index.html')
  
# This is a "sanity check" endpoint. if you can hit this endpoint, then that
# means that the API is running
@app.route('/statuscheck')
def statuscheck():
  json_results = {'ok' : True}
  return json.dumps(json_results)

# POST data to this endoint to store it in Elasticsearch
@app.route('/simulated_event', methods=['POST'])
def simulated_event():
  try:
    if flask.request.method == "POST":
      # print flask.request.get_json()
      # print type(flask.request.get_json())
      # print json.loads(flask.request.get_json())
      store_json(flask.request.get_json(), "simulated_event")
      return json.dumps({'ok' : True})
    else:
      return json.dumps({'ok' : False, 'error' : 'only post requests are allowed to this endpoint'})
  except Exception, e:
    print e
    return json.dumps({'ok' : False})

# POST data to this endoint to store it in Elasticsearch
# Same as /simulated_event
@app.route('/event', methods=['POST'])
def event():
  try:
    if flask.request.method == "POST":
      # print flask.request.get_json()
      # print type(flask.request.get_json())
      # print json.loads(flask.request.get_json())
      store_json(flask.request.get_json(), "event")
      return json.dumps({'ok' : True})
    else:
      return json.dumps({'ok' : False, 'error' : 'only post requests are allowed to this endpoint'})
  except Exception, e:
    print e
    return json.dumps({'ok' : False})

# POST data to this endoint to store it in Elasticsearch
# Same as /simulated_event
@app.route('/reading', methods=['POST'])
def reading():
  try:
    if flask.request.method == "POST":
      # print flask.request.get_json()
      # print type(flask.request.get_json())
      # print json.loads(flask.request.get_json())
      store_json(flask.request.get_json(), "reading")
      return json.dumps({'ok' : True})
    else:
      return json.dumps({'ok' : False, 'error' : 'only post requests are allowed to this endpoint'})
  except Exception, e:
    print e
    return json.dumps({'ok' : False})

# Look up points with this endpoint. Make sure that you send the following arguments in the request
# EX: http://<the ip address or host>/events?minlat=10.0&maxlat=30.0&minlon=40.0&maxlon=70.0
@app.route('/events', methods=['GET'])
def events():
  try:
    if flask.request.method == "GET":
      args = flask.request.args
      print args
      minLat = args["minlat"]
      maxLat = args["maxlat"]
      minLon = args["minlon"]
      maxLon = args["maxlon"]
      minT = 0
      maxT = calendar.timegm(datetime.now().utctimetuple())
      if "minT" in args:
        minT = args["minT"]
      if "maxT" in args:
        maxT = args["maxT"]

      query = build_e3e_event_query(minLat, minLon, maxLat, maxLon)
      res = es.search(index="e3e", doc_type="event", body=query, size=1000)
      hits = res["hits"]["hits"]
      rowList = []
      if len(hits) > 0:
        rowList = map(extract_data, hits)
      return json.dumps({'events' : rowList})
    else:
      return json.dumps({'ok' : False, 'error' : 'only get requests are allowed to this endpoint'})
  except Exception, e:
    print e
    return json.dumps({'ok' : False})

# This is the same as the /events endpoint, except that it looks through all available indexes
# this is probably no longer a viable endpoint because the data that was entered into the database previously
# is no longer available. But it serves as an example for how to chain multiple es_lookup functions
@app.route('/all', methods=['GET'])
def all_data():
  try:
    if flask.request.method == "GET":
      args = flask.request.args
      print args
      minLat = args["minlat"]
      maxLat = args["maxlat"]
      minLon = args["minlon"]
      maxLon = args["maxlon"]
      minT = 0
      maxT = calendar.timegm(datetime.now().utctimetuple())
      if "minT" in args:
        minT = args["minT"]
      if "maxT" in args:
        maxT = args["maxT"]

      query = build_e3e_event_query(minLat, minLon, maxLat, maxLon)
      rowList = es_lookup("e3e", "event", query) + es_lookup("e3e", "simulated_event", query) + es_lookup("external", "kobane", query) + es_lookup("refugee", "refugeecamp", query)
      # the query is the same for both e3e and kobane data
      return json.dumps({'events' : rowList})
    else:
      return json.dumps({'ok' : False, 'error' : 'only get requests are allowed to this endpoint'})
  except Exception, e:
    print e
    return json.dumps({'ok' : False})

# the main function. This actually runs the Flask app
if __name__ == '__main__':
  app.run(host='0.0.0.0')

