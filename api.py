import flask
import json

app = flask.Flask(__name__, static_url_path='')
app.config['DEBUG'] = True

# /statuscheck
@app.route('/statuscheck')
def statuscheck():
  json_results = {'ok' : True}
  return json.dumps(json_results)


if __name__ == '__main__':
  app.run(host='0.0.0.0')
