import flask
import json
import calendar
import ConfigParser
from datetime import datetime, date, time
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

app = flask.Flask(__name__, static_url_path='')
app.config['DEBUG'] = True

parser = ConfigParser.ConfigParser()
parser.read('config.ini')
es_host = parser.get('es', 'host')
es_port = parser.get('es', 'port')

es = Elasticsearch(host=es_host, port=es_port)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

def store_json(blob):
  try:
    print blob
    data = json.loads(blob)
    data['timestamp'] = datetime.fromtimestamp(int(data['timestamp']))
    es.index(index='e3e', doc_type='event', body=data)
    return json.dumps({'ok' : True})
  except Exception, e:
    print "unable to save in elasticsearch"
    print e
    return json.dumps({'ok' : False}, 500)

def extract_data(hit):
  return  hit["_source"]

def build_es_query(minLat, minLon, maxLat, maxLon):
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


@app.route('/')
def root():
  return app.send_static_file('index.html')
  
# /statuscheck
@app.route('/statuscheck')
def statuscheck():
  json_results = {'ok' : True}
  return json.dumps(json_results)

@app.route('/event', methods=['POST'])
def event():
  try:
    if flask.request.method == "POST":
      # print flask.request.get_json()
      # print type(flask.request.get_json())
      # print json.loads(flask.request.get_json())
      store_json(flask.request.get_json())
      return json.dumps({'ok' : True})
    else:
      return json.dumps({'ok' : False, 'error' : 'only post requests are allowed to this endpoint'})
  except Exception, e:
    print e
    return json.dumps({'ok' : False})

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

      query = build_es_query(minLat, minLon, maxLat, maxLon)
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

if __name__ == '__main__':
  app.run(host='0.0.0.0')

