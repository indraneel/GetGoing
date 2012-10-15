import os
from flask import Flask, render_template, request
import simplejson as json
import requests
from busData import stops, routes, shortbus

app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

def getTagStop(tag):
    #print('tag is {}'.format(tag))
    for s in stops:
        #print(stops[s]['tags'])
        if (tag in stops[s]['tags']):
            return s
    return 'not found'

def destOnRoute(route, dest):
    for s in routes[str(route)]['stops']:
        #print('{0} {1}'.format(dest, s))
        if (dest == getTagStop(s)):
            #print('on route')
            return True
    #print('not on route')
    return False 

def getDestETA(route, start, dest, busN=0):
    jsonRt = requests.get('http://nextbus.nodejitsu.com/route/{}'.format(shortbus[route]))
    rt = json.loads(jsonRt.text)
    sindex = -1
    dindex = -1
    print('len(rt) = {}'.format(len(rt)))
    for i in xrange(len(rt)):
        if (start == rt[i]['title']):
            sindex = i
            print('sindex = {}'.format(sindex))
        if (dest == rt[i]['title']):
            dindex = i
            print('dindex = {}'.format(dindex))
    print('have indicies')

    if(sindex == -1 or dindex == -1):
        print('start or destination not found')
        raise NameError('start or destination not found')

    j = sindex
    busNo = busN
    eta = int(rt[j]['predictions'][busNo]['minutes'])
    print('getDestETA eta = {0}, j = {1}'.format(eta, j))
    while (j != dindex):
        print('outer loop')
        j += 1
        if (j >= len(rt)):
            j = 0
            print('j = {0}, dindex = {1}'.format(j, dindex))
        if (rt[j]['predictions'] == None):
            print('null stop')
            continue
        newEta = int(rt[j]['predictions'][busNo]['minutes'])
        while (newEta < eta):
            busNo += 1
            print('busNo = {}'.format(busNo))
            if (busNo >= len(rt[j]['predictions'])):
                print('Out of Buses')
                return 100000
            newEta = int(rt[j]['predictions'][busNo]['minutes'])
        print('new eta')
        eta = newEta
    print('done with getDestETA')
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

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/search', methods=['POST', 'GET'])
def nextBus():

    if request.method == 'POST':
        startLoc = request.form.get('start', '')
        print(startLoc)
        destLoc = request.form.get('destination', '')
        print(destLoc)
        lat = request.form.get('latitude', '')
        print(lat)
        lon = request.form.get('longitude', '')
        print(lon)
    else:
        startLoc = request.args.get('start', '')
        print(startLoc)
        destLoc = request.args.get('destination', '')
        print(destLoc)        
        lat = request.args.get('latitude', '')
        print(lat)
        lon = request.args.get('longitude', '')
        print(lon)

    # if(true):
    # print(lat)
    nearJSON = requests.get('http://nextbus.nodejitsu.com/nearby/{}/{}'.format(lat, lon))
    nearby = json.loads(nearJSON.text)
    print(nearby)
    # else:
    #     nearby = [startLoc]
    #     lat = float(stops[startLoc]['lat'])
    #     lon = float(stops[startLoc]['lon'])
    
    next = 100000 # next bus eta
    eta = 100000 # destination eta
    nextbus = ''
    start = ''
    walk1 = 100000

    for stop in nearby:
        walktemp = getWalkTime(lat, lon, stop)

        print(stop)
        sJSON = requests.get('http://nextbus.nodejitsu.com/stop/'+stop)
        buses = json.loads(sJSON.text)
        print(buses)
        for b in buses:
            print (b)
            if (b['predictions'] == None):
                print('no predictions')
                continue
            pred = int(b['predictions'][0]['minutes'])
            bus = b['title']
            if (not destOnRoute(bus, destLoc)):
                print('not on route')
                continue
            busNo = 0
            busNoFail = False # True if you run out of buses
            print('busNo = {}'.format(busNo))
            while(pred < walktemp-1):
                busNo += 1
                print('busNo = {}'.format(busNo))
                if (busNo >= len(b['predictions'])):
                    print('Out of Buses')
                    busNoFail = True
                    break
                pred = int(b['predictions'][busNo]['minutes'])
            if (busNoFail):
                continue
            eta2 = getDestETA(bus, stop, destLoc, busNo)
            print(bus) #bus
            print(eta2) #bus ETA
            if (eta2 < eta or (eta2 == eta and walktemp < walk1)):
                next = pred
                eta = eta2
                print('faster bus')
                nextbus = b['title']
                start = stop
                walk1 = walktemp
        print('checked buses in stop {}'.format(stop))

    # walk1 = getWalkTime(40.48474, -74.43672, startLoc)
    print('loop done')
    leave = next - walk1 - 1
    if (leave < 0):
        leave = "OH SHIT RUN"
    # print('done')
    return render_template('nextdest.html', bus=nextbus, start=start, smins=next, dest=destLoc, dmins=eta, walk1 = walk1, leave=leave)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)