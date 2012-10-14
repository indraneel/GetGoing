from flask import Flask, render_template
import simplejson as json
import requests
import busData
app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

@app.route('/<start>/')
def nextBus(start):
    s = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(start))
    # d = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(dest))
    jsonData = json.loads(s.text)
    next = 1000
    nextbus = ''
    for b in jsonData:
    	if (b['predictions']==None):
    		continue
    	pred = int(b['predictions'][0]['minutes'])
        bus = b['title']
        if (not destOnRoute(bus, dest)):
            continue

    	print(bus) #bus
    	print(pred) #bus ETA
    	if (pred < next):
    		next = pred
    		print('faster bus')
    		bus = b['title']
    return render_template('next.html', bus=nextbus, mins=next)

if __name__ == '__main__':
    app.run(debug=True)

def getTagStop(tag):
    for s in stops:
        if (tag in s['tags']):
            return s
    return 'not found'

def destOnRoute(route, dest):
    for s in routes[route]:
        if (dest == getTagStop(s)):
            return True
    return False 