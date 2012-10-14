from flask import Flask, render_template
import simplejson as json
import requests
from busData import stops, routes, shortbus

app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

def getTagStop(tag):
    # print('tag is {}'.format(tag))
    for s in stops:
        # print(stops[s]['tags'])
        if (tag in stops[s]['tags']):
            return s
    return 'not found'

def destOnRoute(route, dest):
    for s in routes[str(route)]['stops']:
        # print('{0} {1}'.format(dest, s))
        if (dest == getTagStop(s)):
            # print('on route')
            return True
    # print('not on route')
    return False 

def getDestETA(route, start, dest):
    jsonRt = requests.get('http://nextbus.nodejitsu.com/route/{}'.format(shortbus[route]))
    rt = json.loads(jsonRt.text)
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
    eta = int(rt[j]['predictions'][busNo]['minutes'])
    while (j != dindex):
        j += 1
        if (j >= len(rt)):
            j = 0
        newEta = int(rt[j]['predictions'][busNo]['minutes'])
        while (newEta < eta):
            busNo += 1
            newEta = int(rt[j]['predictions'][busNo]['minutes'])
        eta = newEta
    return eta


@app.route('/<start>')
def nextBus(start):
    s = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(start))
    # d = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(dest))
    jsonData = json.loads(s.text)
    dest = "Hill Center"
    next = 1000 # next bus eta
    eta = 1000 # destination eta
    nextbus = ''
    for b in jsonData:
        if (b['predictions']==None):
            continue
        pred = int(b['predictions'][0]['minutes'])
        bus = b['title']
        if (not destOnRoute(bus, dest)):
            continue
         
        eta2 = getDestETA(bus, start, dest)
        print(bus) #bus
        print(eta2) #bus ETA
        if (eta2 < eta):
            next = pred
            eta = eta2
            print('faster bus')
            nextbus = b['title']

    return render_template('nextdest.html', bus=nextbus, start=start, smins=next, dest=dest, dmins=eta)

if __name__ == '__main__':
    app.run(debug=True)
