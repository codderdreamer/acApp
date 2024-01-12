from flask import Flask, render_template, request, jsonify

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, static_url_path='',
                         static_folder='client/build',
                         template_folder='client/build')
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/admin/dashboard")
        def dashboard():
            return render_template("index.html")

        @self.app.route("/admin/software")
        def software():
            return render_template("index.html")

        @self.app.route("/")
        def hera():
            return render_template("index.html")

        @self.app.route('/get_flask_ip', methods=['GET'])
        def get_flask_ip():
            ip_address = request.environ.get('REMOTE_ADDR')
            return jsonify({'ip': ip_address})

    def run(self):
        self.app.run(use_reloader=True, host='0.0.0.0', port=80, threaded=True)


    