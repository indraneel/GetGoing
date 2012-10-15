from flask import Flask, render_template
import requests
import simplejson as json

app = Flask(__name__)

@app.route('/<v1>&<v2>')
def route(v1, v2):
    return render_template('test.html', data=v2)

if __name__ == '__main__':
    app.run()