from flask import Flask, render_template
import simplejson as json
import requests
app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

@app.route('/<stop>')
def hello_world(stop):
    r = requests.get('http://nextbus.nodejitsu.com/route/{}'.format(stop))
    jsonData = json.loads(r.text)
    print jsonData
    return render_template('home.html', data=jsonData)



if __name__ == '__main__':
    app.run(debug=True)
