from flask import Flask, render_template
import simplejson as json
import requests
import busData

app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

@app.route('/<start>')
def nextBus(start):
    s = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(start))
    # d = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(dest))
    jsonData = json.loads(s.text)
    dest = "Hill Center"
    next = 1000
    bus = ''
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

    return render_template('nextdest.html', start=bus, smins=next, dest=dest, dmins=eta)

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

def getDestETA(route, start, dest):
    rt = requests.get('http://nextbus.nodejitsu.com/route/{}'.format(route))
    sindex = -1
    dindex = -1
    for i in xrange(len(rt)):
        if (start == rt[i]['title']):
            sindex = i
        if (dest == rt[i]['title']):
            dindex = i

    if(sindex == -1 or dindex == -1):
        print('start or destination not found')
        raise NameError('start or destination not found')

    j = sindex
    busNo = 0
    eta = rt[j]['predictions'][busNo]['minutes']
    while (j != dindex):
        j += 1
        if (j >= len(rt)):
            j = 0
        newEta = rt[j]['predictions'][busNo]['minutes']
        while (newEta < eta):
            busNo += 1
            newEta = rt[j]['predictions'][busNo]['minutes']
        eta = newEta
    return eta



