from flask import Flask, render_template
import simplejson as json
import requests
app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

@app.route('/')
def main():
    return render_template('base.html')

@app.route('/stop/<stop>')
def nextBus(stop):
    r = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(stop))
    jsonData = json.loads(r.text)
    next = 1000
    bus = ''
    for b in jsonData:
    	if (b['predictions']==None):
    		continue
    	pred = int(b['predictions'][0]['minutes'])
    	print(b['title'])
    	print(pred)
    	if (pred < next):
    		next = pred
    		print('faster bus')
    		bus = b['title']
    return render_template('base.html', bus=bus, mins=next)

if __name__ == '__main__':
    app.run(debug=True)
