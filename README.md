GetGoing
========

![You can see a screenshot of it here](http://i.imgur.com/dpaoz.png)

What it does
------------

GetGoing (or /GET/Going) is a more human-readable interface for Rutgers' NextBus system.  Where NextBus requires you to know the route and stop you want, GetGoing lets Rutgers students and faculty input their desired bus stop and get back the quickest bus route to take, the time it will take for their bus to reach their stop, how long it will take them to walk to the bus stop and when they should leave to catch their bus, based on where they are!

How it does 
-----------

All the routing/server stuff is done in Python via the Flask microframework.  The front-end was done with Zurb's Foundation framework, HTML5 for the geolocation and JavaScript to properly get the lat/long coordinates into the inputs. GetGoing hooks into the Rutgers API and the Google Maps API for bus and walking directions/times, respectively.

Coming Soon
-----------
* Autocompleting search of all the buildings on the Rutgers New Brunswick campus.
* Better mobile responsiveness
* Selection of starting location

Planned Features (hopefully soon)
---------------------------------
* Options on when to get going (the next few possibilities and arrival times)
* Lazy mode (least possible walking distance)
* One page website
