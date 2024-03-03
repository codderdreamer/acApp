import os
import time
from flask import Flask, render_template, request, jsonify
from threading import Thread
import threading

class FlaskModule:
    def __init__(self,application) -> None:
        self.application = application
        self.host = '0.0.0.0'
        self.app = Flask(__name__, static_url_path='',
                         static_folder='../client/build',
                         template_folder='../client/build')
        self.setup_routes()
        
    def setup_routes(self):
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
        
