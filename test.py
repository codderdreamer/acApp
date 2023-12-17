
import os
import time
from flask import Flask, render_template, request


app = Flask(__name__, static_url_path='',
                  static_folder='client/build',
                  template_folder='client/build')

@app.route("/")
def hera():
    return render_template("index.html")


app.run(use_reloader=True, host='0.0.0.0', port=80, threaded=True)
    
while True:
    time.sleep(1)