from flask import Flask, render_template
import simplejson
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html', variable="asdf")

if __name__ == '__main__':
    app.run(debug=True)
