import os
import time
from flask import Flask, render_template, request, jsonify, make_response
from threading import Thread
import threading
from werkzeug.security import check_password_hash

class FlaskModule:
    def __init__(self,application) -> None:
        self.application = application
        self.host = '0.0.0.0'
        self.app = Flask(__name__, static_url_path='',
                         static_folder='../client/build',
                         template_folder='../client/build')
        self.setup_routes()
        
    def setup_routes(self):


        
        
        @self.app.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            UserName = data.get('UserName')
            Password = data.get('Password')
            
            login = self.application.databaseModule.get_user_login()
            if login["UserName"] == UserName and login["Password"] == Password:
                
                @self.app.route("/")
                def hera():
                    return render_template("index.html")
                
                @self.app.route("/admin/dashboard")
                def dashboard():
                    return render_template("index.html")

                @self.app.route("/admin/quick-setup")
                def quick():
                    return render_template("index.html")

                @self.app.route("/admin/charging")
                def charging():
                    return render_template("index.html")

                @self.app.route("/admin/hardware")
                def hardware():
                    return render_template("index.html")

                @self.app.route("/admin/software")
                def software():
                    return render_template("index.html")

                @self.app.route("/admin/status")
                def status():
                    return render_template("index.html")
                
                @self.app.route("/admin/profile")
                def profile():
                    return render_template("index.html")
            
                return jsonify({'message': 'Login successful'})
            else:
                return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm="Login required!"'})
        

            
        
        
        @self.app.route('/changeProfile', methods=['POST'])
        def changeProfile():
            data = request.get_json()
            Password = data.get('Password')
            NewPassword = data.get('NewPassword')
            
            print(self.application.databaseModule.get_user_login())
            
            if self.application.databaseModule.get_user_login()["Password"] == Password:
            
                result = self.application.databaseModule.set_password(NewPassword)
                
                if result:
                    return jsonify({'message': 'Login successful'})
                else:
                    return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm="Login required!"'})
            else:
                return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    def run(self):
        self.app.run(use_reloader=False, host=self.host, port=80, threaded=True)
        
class FlaskModuleThread(threading.Thread):
    def __init__(self,application):
        super().__init__()
        self.stop_event = threading.Event()
        self.application = application
        self.flaskModule = FlaskModule(self.application)

    def stop(self):
        self.stop_event.set()

    def run(self):
        if not self.stop_event.is_set():
            print("FlaskModuleThread çalıştırıldı.")
            self.flaskModule.run()
        print("FlaskModuleThread durduruldu.")
        
