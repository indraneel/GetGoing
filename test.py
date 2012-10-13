from flask import Flask, render_template
import requests
import simplejson as json

app = Flask(__name__)

@app.route('/')
def route():
    r = requests.get('http://nextbus.nodejitsu.com/route/a')
    # return render_template('test.html', data=str(len(json.load(r))))
    return render_template('test.html', data=yup)

if __name__ == '__main__':
    app.run()