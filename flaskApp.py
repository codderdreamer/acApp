
import os
import time
from flask import Flask, render_template, request, jsonify
from threading import Thread

app = Flask(__name__, static_url_path='',
                  static_folder='client/build',
                  template_folder='client/build')

@app.route("/admin/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/admin/software")
def software():
    return render_template("index.html")

@app.route("/")
def hera():
    return render_template("index.html")

@app.route('/get_flask_ip', methods=['GET'])
def get_flask_ip():
    ip_address = request.environ.get('REMOTE_ADDR')
    return jsonify({'ip': ip_address})

app.run(use_reloader=True, host='0.0.0.0', port=80, threaded=True)
while True:
    time.sleep(1)

    