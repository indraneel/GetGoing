from flask import Flask, render_template, request
import simplejson as json
import requests
from busData import stops, routes, shortbus

app = Flask(__name__)
api_urls = {'nextbus': 'http://nextbus.nodejitsu.com/'}

def getTagStop(tag):
    # #print('tag is {}'.format(tag))
    for s in stops:
        # #print(stops[s]['tags'])
        if (tag in stops[s]['tags']):
            return s
    return 'not found'

def destOnRoute(route, dest):
    for s in routes[str(route)]['stops']:
        # #print('{0} {1}'.format(dest, s))
        if (dest == getTagStop(s)):
            # #print('on route')
            return True
    # #print('not on route')
    return False 

def getDestETA(route, start, dest, busN=0):
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
        #print('start or destination not found')
        raise NameError('start or destination not found')

    j = sindex
    busNo = busN
    eta = int(rt[j]['predictions'][busNo]['minutes'])
    while (j != dindex):
        j += 1
        if (j >= len(rt)):
            j = 0
        try:
            newEta = int(rt[j]['predictions'][busNo]['minutes'])
        except IndexError:
            #print('Index Error at j={0} busNo={1}'.format(j, busNo))
            return 100000
        while (newEta < eta):
            busNo += 1
            try:
                newEta = int(rt[j]['predictions'][busNo]['minutes'])
            except IndexError:
                #print('Index Error at j={0} busNo={1}'.format(j, busNo))
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

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/search', methods=['POST', 'GET'])
def nextBus():

    if request.method == 'POST':
        startLoc = request.form.get('start', '')
        #print(startLoc)
        destLoc = request.form.get('destination', '')
        #print(destLoc)
        lat = request.form.get('latitude', '')
        #print(lat)
        lon = request.form.get('longitude', '')
        #print(lon)
    else:
        startLoc = request.args.get('start', '')
        #print(startLoc)
        destLoc = request.args.get('destination', '')
        #print(destLoc)        
        lat = request.args.get('latitude', '')
        #print(lat)
        lon = request.args.get('longitude', '')
        #print(lon)

    # if(true):
    #print(lat)
    nearJSON = requests.get('http://nextbus.nodejitsu.com/nearby/{}/{}'.format(lat, lon))
    nearby = json.loads(nearJSON.text)
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

        #print(stop)
        sJSON = requests.get('http://nextbus.nodejitsu.com/stop/'+stop)
        buses = json.loads(sJSON.text)
        for b in buses:
            if (b['predictions']==None):
                #print('no predictions')
                continue
            pred = int(b['predictions'][0]['minutes'])
            bus = b['title']
            if (not destOnRoute(bus, destLoc)):
                #print('not on route')
                continue
            busNo = 0
            while(pred < walktemp-1):
                busNo += 1
                try:
                    pred = int(b['predictions'][busNo]['minutes'])
                except IndexError:
                    #print('Index Error at j={0} busNo={1}'.format(j, busNo))
                    return 100000
             
            eta2 = getDestETA(bus, stop, destLoc, busNo)
            #print(bus) #bus
            #print(eta2) #bus ETA
            if (eta2 < eta):
                next = pred
                eta = eta2
                #print('faster bus')
                nextbus = b['title']
                start = stop
                walk1 = walktemp

    # walk1 = getWalkTime(40.48474, -74.43672, startLoc)

    leave = next - walk1 - 1
    if (leave < 0):
        leave = "OH SHIT LEAVE NOW!"
    return render_template('nextdest.html', bus=nextbus, start=start, smins=next, dest=destLoc, dmins=eta, walk1 = walk1, leave=leave)


    # s = requests.get('http://nextbus.nodejitsu.com/stop/'+startLoc)
    # # d = requests.get('http://nextbus.nodejitsu.com/stop/{}'.format(dest))
    # jsonData = json.loads(s.text)
    # next = 100000 # next bus eta
    # eta = 100000 # destination eta
    # nextbus = ''
    # for b in jsonData:
    #     if (b['predictions']==None):
    #         continue
    #     pred = int(b['predictions'][0]['minutes'])
    #     bus = b['title']
    #     if (not destOnRoute(bus, destLoc)):
    #         continue
         
    #     eta2 = getDestETA(bus, startLoc, destLoc)
    #     #print(bus) #bus
    #     #print(eta2) #bus ETA
    #     if (eta2 < eta):
    #         next = pred
    #         eta = eta2
    #         #print('faster bus')
    #         nextbus = b['title']

    # walk1 = getWalkTime(40.48474,  -74.43672, startLoc)

    # leave = next - walk1 - 1

    # return render_template('nextdest.html', bus=nextbus, start=startLoc, smins=next, dest=destLoc, dmins=eta, walk1 = walk1, leave=leave)

# @app.route('/geo', methods=['POST', 'GET'])
# def nextBus():

#     if request.method == 'POST':
#         lat = request.form.get('lat', '')
#         #print(lat)
#         lon = request.form.get('lon', '')
#         #print(lon)
#         destLoc = request.form.get('destination', '')
#         #print(destLoc)
#     else:
#         startLoc = request.args.get('start', '')
#         #print(startLoc)
#         destLoc = request.args.get('destination', '')
#         #print(destLoc)        

#     nearJSON = requests.get('http://nextbus.nodejitsu.com/nearby/{0}/{1}'.format(lat, lon))
#     nearby = json.loads(nearjson.text)
#     next = 100000 # next bus eta
#     eta = 100000 # destination eta
#     nextbus = ''
#     start = ''
#     walk1 = 100000

#     for stop in nearby:
#         walktemp = getWalkTime(lat, lon, stop)

#         sJSON = requests.get('http://nextbus.nodejitsu.com/stop/'+startLoc)
#         buses = json.loads(sJSON.text)
#         for b in buses:
#             if (b['predictions']==None):
#                 continue
#             pred = int(b['predictions'][0]['minutes'])
#             bus = b['title']
#             if (not destOnRoute(bus, destLoc)):
#                 continue
#             busNo = 0
#             while(pred < walktemp):
#                 busNo += 1
#                 try:
#                     newEta = int(rt[j]['predictions'][busNo]['minutes'])
#                 except IndexError:
#                     #print('Index Error at j={0} busNo={1}'.format(j, busNo))
#                     return 100000
             
#             eta2 = getDestETA(bus, startLoc, destLoc, busNo)
#             #print(bus) #bus
#             #print(eta2) #bus ETA
#             if (eta2 < eta):
#                 next = pred
#                 eta = eta2
#                 #print('faster bus')
#                 nextbus = b['title']
#                 start = stop
#                 walk1 = walktemp

#     walk1 = getWalkTime(40.48474,  -74.43672, startLoc)

#     leave = next - walk1 - 1

#     return render_template('nextdest.html', bus=nextbus, start=startLoc, smins=next, dest=destLoc, dmins=eta, walk1 = walk1, leave=leave)

if __name__ == '__main__':
    app.run(debug=True)
