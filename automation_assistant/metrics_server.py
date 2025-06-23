from flask import Flask, Response
from automation_assistant.guardrails import LatencyMetrics

app = Flask(__name__)
metrics = LatencyMetrics()  # Make sure this is the same object from main!

@app.route("/metrics")
def metrics_endpoint():
    return Response(metrics.export_prometheus(), mimetype="text/plain")
