import time

from flask import Flask, Response
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Métrica principal: cuenta cuántas solicitudes ha recibido la aplicación.
# Labels: method (verbo HTTP), endpoint (ruta visitada), status (código de respuesta)
http_requests_total = Counter(
    "http_requests_total",
    "Total de solicitudes HTTP recibidas",
    ["method", "endpoint", "status"],
)

# Métrica opcional: un valor que sube y baja (Gauge), a diferencia del Counter
# de arriba que solo crece. Representa cuántas solicitudes está procesando la
# app EN ESTE MOMENTO. Es una métrica real que se usa en producción para ver
# concurrencia y detectar cuellos de botella.
app_requests_in_progress = Gauge(
    "app_requests_in_progress",
    "Cantidad de solicitudes que la app está procesando en este momento",
)


@app.route("/")
def hello():
    app_requests_in_progress.inc()
    try:
        # Trabajo simulado, solo para que la solicitud tarde lo suficiente
        # y se pueda observar el Gauge subiendo durante la demo.
        time.sleep(2)
        http_requests_total.labels(method="GET", endpoint="/", status="200").inc()
        return "Hello World"
    finally:
        app_requests_in_progress.dec()


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # 0.0.0.0 en lugar de 127.0.0.1: dentro del contenedor, 127.0.0.1 solo acepta
    # conexiones que se originan en el propio contenedor. Docker necesita que la
    # app escuche en todas las interfaces (0.0.0.0) para poder mapear el puerto
    # hacia el host y para que Prometheus la alcance desde otro contenedor.
    # threaded=True: permite que la app atienda varias solicitudes en paralelo,
    # necesario para que app_requests_in_progress pueda mostrar un valor mayor a 1.
    app.run(host="0.0.0.0", port=8000, threaded=True)
