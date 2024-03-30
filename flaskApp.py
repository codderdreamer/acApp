
import os
import time
from flask import Flask, render_template, request, jsonify
from threading import Thread
from flask import Flask, request, jsonify, make_response
from werkzeug.security import check_password_hash

app = Flask(__name__, static_url_path='',
                  static_folder='client/build',
                  template_folder='client/build')

@app.route("/")
def hera():
    return render_template("index.html")

@app.route("/admin/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/admin/quick-setup")
def quick():
    return render_template("index.html")

@app.route("/admin/charging")
def charging():
    return render_template("index.html")

@app.route("/admin/hardware")
def hardware():
    return render_template("index.html")

@app.route("/admin/software")
def software():
    return render_template("index.html")

@app.route("/admin/status")
def status():
    return render_template("index.html")

@app.route("/admin/profile")
def profile():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    UserName = data.get('UserName')
    Password = data.get('Password')
    
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = users.get(auth.username)
    
    # Kullanıcı adı ve parola kontrolü
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    if user == auth.password:
        # Kullanıcı adı ve parola doğru
        return jsonify({'message': 'Login successful'})
    else:
        # Kullanıcı adı veya parola yanlış
        return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
# @app.route('/get_flask_ip', methods=['GET'])
# def get_flask_ip():
#     ip_address = request.environ.get('REMOTE_ADDR')
#     return jsonify({'ip': ip_address})

app.run(use_reloader=True, host='0.0.0.0', port=80, threaded=True)
while True:
    time.sleep(1)

    