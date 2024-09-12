import os
import time
from flask import Flask, render_template, request, jsonify, session, make_response
from threading import Thread
import threading
from werkzeug.security import check_password_hash
import jwt
import datetime
from functools import wraps

class FlaskModule:
    def __init__(self,application) -> None:
        self.application = application
        self.host = '0.0.0.0'
        self.app = Flask(__name__, static_url_path='',
                         static_folder='../client/build',
                         template_folder='../client/build')
        self.app.secret_key = 'myS3cr3tK3y_2024!@#$'
        self.setup_routes()
        
    def token_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'authenticated' not in session:
                return jsonify({'message': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        return decorated
        
    def setup_routes(self):
        @self.app.route("/")
        def hera():
            return render_template("index.html")

        @self.app.route("/admin/dashboard")
        @self.token_required
        def dashboard():
            return render_template("index.html")

        @self.app.route("/admin/quick-setup")
        @self.token_required
        def quick():
            return render_template("index.html")

        @self.app.route("/admin/charging")
        @self.token_required
        def charging():
            return render_template("index.html")

        @self.app.route("/admin/hardware")
        @self.token_required
        def hardware():
            return render_template("index.html")

        @self.app.route("/admin/software")
        @self.token_required
        def software():
            return render_template("index.html")

        @self.app.route("/admin/status")
        @self.token_required
        def status():
            return render_template("index.html")
        
        @self.app.route("/admin/profile")
        @self.token_required
        def profile():
            return render_template("index.html")
        
        @self.app.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            UserName = data.get('UserName')
            Password = data.get('Password')
            
            login = self.application.databaseModule.get_user_login()
            if login["UserName"] == UserName and login["Password"] == Password:   
                session['authenticated'] = True
                session['UserName'] = UserName
                return jsonify({'message': 'Login successful'})
            else:
                return jsonify({'message': 'Invalid username or password'}), 401
              
        
        # @self.app.route('/login', methods=['POST'])
        # def login():
        #     data = request.get_json()
        #     UserName = data.get('UserName')
        #     Password = data.get('Password')
            
        #     # Assume authentication is successful
        #     # You should perform actual authentication here
        #     session['authenticated'] = True
        #     session['UserName'] = UserName

        #     return jsonify({'message': 'Login successful'})
            
        
        
        @self.app.route('/changeProfile', methods=['POST'])
        @self.token_required
        def changeProfile():
            data = request.get_json()
            Password = data.get('Password')
            NewPassword = data.get('NewPassword')
            
            if self.application.databaseModule.get_user_login()["Password"] == Password:
                result = self.application.databaseModule.set_password(NewPassword)
                
                if result:
                    return jsonify({'message': 'Password changed successfully'})
                else:
                    return jsonify({'message': 'Failed to change password'}), 500
            else:
                return jsonify({'message': 'Invalid password'}), 401
    
    def run(self):
        self.app.run(use_reloader=False, host=self.host, port=80, threaded=True)
        
class FlaskModuleThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.application = None
        self.flaskModule = FlaskModule(self.application)

    def stop(self):
        self.stop_event.set()

    def run(self):
        if not self.stop_event.is_set():
            print("FlaskModuleThread çalıştırıldı.")
            self.flaskModule.run()
        print("FlaskModuleThread durduruldu.")
        