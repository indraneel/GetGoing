from flask import Flask, render_template
import simplejson as json
import requests
app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

@app.route('/stop/<route>')
def hello_world(route):
    r = requests.get('http://nextbus.nodejitsu.com/route/{}'.format(route))
    jsonData = json.loads(r.text)
    return render_template('home.html', data=jsonData[0]['predictions'][0]['minutes'])

if __name__ == '__main__':
    app.run(debug=True)
