import flask
import json
import ConfigParser
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
    es.index(index='test', doc_type='explosion', body=json.loads(blob))
    return json.dumps({'ok' : True})
  except Exception, e:
    print "unable to save in elasticsearch"
    print e
    return json.dumps({'ok' : False}, 500)

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
    

if __name__ == '__main__':
  app.run(host='0.0.0.0')

