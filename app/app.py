from flask import Flask, Response
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random

app = Flask(__name__)

# Métrica principal: cuenta cuántas solicitudes ha recibido la aplicación.
# Labels: method (verbo HTTP), endpoint (ruta visitada), status (código de respuesta)
http_requests_total = Counter(
    "http_requests_total",
    "Total de solicitudes HTTP recibidas",
    ["method", "endpoint", "status"],
)

# Métrica opcional: un valor que sube y baja con el tiempo (Gauge),
# útil para mostrar que Prometheus guarda una serie temporal, no solo un contador.
app_temperature_celsius = Gauge(
    "app_temperature_celsius",
    "Temperatura simulada de la aplicación (valor de ejemplo para la demo)",
)


@app.route("/")
def hello():
    http_requests_total.labels(method="GET", endpoint="/", status="200").inc()
    app_temperature_celsius.set(round(random.uniform(20.0, 30.0), 1))
    return "Hello World"


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # 0.0.0.0 en lugar de 127.0.0.1: dentro del contenedor, 127.0.0.1 solo acepta
    # conexiones que se originan en el propio contenedor. Docker necesita que la
    # app escuche en todas las interfaces (0.0.0.0) para poder mapear el puerto
    # hacia el host y para que Prometheus la alcance desde otro contenedor.
    app.run(host="0.0.0.0", port=8000)
