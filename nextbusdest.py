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
        try:
            newEta = int(rt[j]['predictions'][busNo]['minutes'])
        except IndexError:
            print('Index Error at j={0} busNo={1}'.format(j, busNo))
            return 100000
        while (newEta < eta):
            busNo += 1
            try:
                newEta = int(rt[j]['predictions'][busNo]['minutes'])
            except IndexError:
                print('Index Error at j={0} busNo={1}'.format(j, busNo))
                return 100000
        eta = newEta
    return eta

def getWalkTime(lat, lon, stop):
    jsonGmaps = requests.get('http://maps.googleapis.com/maps/api/distancematrix/json?origins={0},%20{1}&destinations={2},%20{3}&mode=walking&sensor=false'.format(lat, lon, float(stops[stop]['lat']), float(stops[stop]['lon'])))
    gmaps = json.loads(jsonGmaps.text)
    strtime = gmaps['rows'][0]['elements'][0]['duration']['text']
    time = int(strtime.split(' ')[0])
    return time

def getWalkTimeAd(stop, address):
    jsonGmaps = requests.get('http://maps.googleapis.com/maps/api/distancematrix/json?origins={0},%20{1}&destinations={2}&mode=walking&sensor=false'.format(float(stops[stop]['lat']), float(stops[stop]['lon']), address))
    gmaps = json.loads(jsonGmaps.text)
    strtime = gmaps['rows'][0]['elements'][0]['duration']['text']
    time = int(strtime.split(' ')[0])
    return time


@app.route('/start=<start>&destination=<dest>')
def nextBus(start, dest):
    s = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(start))
    # d = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(dest))
    jsonData = json.loads(s.text)
    next = 100000 # next bus eta
    eta = 100000 # destination eta
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

    walk1 = getWalkTime(40.48474,  -74.43672, start)

    return render_template('nextdest.html', bus=nextbus, start=start, smins=next, dest=dest, dmins=eta, walk1 = walk1)

if __name__ == '__main__':
    app.run(debug=True)
