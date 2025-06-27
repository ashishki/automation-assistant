# automation_assistant/metrics_server.py

from flask import Flask, Response

class MetricsServer:
    def __init__(self, metrics):
        self.metrics = metrics
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/metrics")
        def metrics_endpoint():
            return Response(self.metrics.export_prometheus(), mimetype="text/plain")

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)

