# Observability Demo — Flask + Prometheus

Demo mínimo para una charla introductoria de observabilidad. Todo corre en Docker:
no necesitas instalar Python, Flask ni nada más en tu máquina. Solo Docker Desktop.

## Idea central

```
Navegador → localhost:8000 → App Flask (contenedor) → /metrics
                                                          ↑
                                          Prometheus (contenedor) → localhost:9090
```

Una aplicación produce información sobre su comportamiento → esa información se
convierte en métricas → Prometheus las recolecta (Pull) → podemos consultarlas con PromQL.

## Estructura del proyecto

```
Prometheus-Demo/
├── docker-compose.yml
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── prometheus/
    └── prometheus.yml
```

## Requisitos

- Docker Desktop instalado y **ejecutándose**. Nada más.

## Cómo ejecutar (Windows / PowerShell)

Si ya tienes esta carpeta (clonada o copiada), abre PowerShell dentro de ella y ejecuta:

```powershell
docker compose up --build
```

Espera a ver en la terminal que Flask y Prometheus arrancaron. Deja la ventana abierta
(los logs se muestran en vivo).

Para ejecutar en segundo plano (recomendado si vas a seguir usando la misma terminal
para otros comandos durante la charla):

```powershell
docker compose up --build -d
```

### Verificación

1. Abre `http://localhost:8000/` → debe mostrar `Hello World`.
2. Abre `http://localhost:8000/metrics` → debe mostrar texto plano con métricas,
   incluyendo `http_requests_total`.
3. Abre `http://localhost:9090/` → interfaz web de Prometheus.
4. En Prometheus, ve a **Status → Targets** y confirma que el target `flask-app` (`app:8000`)
   está en estado **UP**.
5. En la caja de consultas de Prometheus, ejecuta:

   ```
   http_requests_total
   ```

   Deberías ver una o más series con labels `method`, `endpoint`, `status`.

### Detener el proyecto

```powershell
docker compose down
```

## Guion de la demo (~10 minutos)

### 1. Introducción (1 min)

> "Tenemos una aplicación funcionando. Pero una pregunta importante es: ¿cómo podemos
> saber qué está ocurriendo dentro de ella? ¿Cuántas visitas recibe? ¿Está funcionando bien?
> Eso es observabilidad, y hoy vamos a verlo con un ejemplo mínimo usando Prometheus."

### 2. La aplicación (1-2 min)

Abrir `http://localhost:8000/`.

> "Esto es una aplicación real, corriendo dentro de un contenedor Docker. Docker aquí
> es solo la caja donde vive la aplicación — no necesitamos entender Docker a fondo
> para seguir la demo."

Muestra `Hello World`.

### 3. Las métricas (2-3 min)

Abrir `http://localhost:8000/metrics`.

> "Esta aplicación no solo responde 'Hello World'. También expone un segundo endpoint,
> `/metrics`, donde publica información sobre su propio comportamiento."

Señala una línea como:

```
http_requests_total{method="GET",endpoint="/",status="200"} 5
```

Explica:
- **Nombre de la métrica**: `http_requests_total` — cuenta cuántas solicitudes ha recibido.
- **Labels**: `method`, `endpoint`, `status` — permiten desglosar la métrica (¿de qué tipo
  de solicitud hablamos?).
- **Valor**: el número de veces que esto ha ocurrido hasta ahora.

### 4. Prometheus (1-2 min)

Abrir `http://localhost:9090/`.

> "Prometheus es un servidor que, cada pocos segundos, visita el endpoint `/metrics` de
> nuestra aplicación y guarda esos valores. A esto se le llama modelo *Pull*: Prometheus
> pregunta activamente, en lugar de esperar a que la aplicación le envíe datos."

Si quieres, muestra brevemente **Status → Targets** y el target `app:8000` en UP.

> "Un detalle rápido: dentro del contenedor de Prometheus, `localhost` se refiere al
> propio Prometheus, no a la app. Por eso usamos el nombre del servicio de Docker Compose,
> `app`, para que Prometheus la encuentre en la red interna."

(No profundices más en redes Docker — es un detalle, no el foco de la charla.)

### 5. PromQL (1-2 min)

En la caja de consultas de Prometheus, ejecutar:

```
http_requests_total
```

> "Esto es PromQL: una forma de hacer preguntas sobre las métricas que Prometheus ha
> almacenado. Aquí estamos preguntando: ¿cuál es el valor actual de `http_requests_total`?"

Opcional, para mostrar filtrado por label:

```
http_requests_total{endpoint="/"}
```

> "Aquí filtramos solo las solicitudes al endpoint `/`."

### 6. El cambio en vivo (2-3 min)

Vuelve al navegador y visita varias veces `http://localhost:8000/`.

Regresa a Prometheus y vuelve a ejecutar:

```
http_requests_total
```

> "Fíjense que el valor subió. Este es el flujo completo:
> 1. Ustedes visitan la aplicación.
> 2. La aplicación recibe la solicitud.
> 3. La métrica se incrementa internamente.
> 4. Prometheus, cada pocos segundos, consulta `/metrics` de nuevo.
> 5. Prometheus guarda el nuevo valor.
> 6. Nosotros lo consultamos con PromQL.
>
> Esto es, en esencia, cómo funciona un sistema de monitoreo basado en Prometheus."

### 7. Bonus: una métrica que sube y baja (si sobra tiempo, 1-2 min)

`http_requests_total` solo crece — es un **Counter**. Prometheus también soporta
**Gauges**: valores que pueden subir y bajar. El demo incluye uno: `app_requests_in_progress`,
que representa cuántas solicitudes está procesando la app *en este preciso momento*
(una métrica real, muy usada en producción para ver concurrencia).

Para mostrarlo en vivo, abre 3-4 pestañas del navegador y carga
`http://localhost:8000/` casi al mismo tiempo en todas (la app tarda ~2 segundos en
responder a propósito, para dar tiempo a observar el valor). Mientras se están
procesando, ejecuta en Prometheus:

```
app_requests_in_progress
```

> "Miren, el valor subió a 3 o 4 mientras esas solicitudes se procesaban al mismo
> tiempo. En unos segundos, cuando todas terminen, va a volver a 0. Esto es un Gauge:
> a diferencia del contador de antes, este valor sube **y baja**, y refleja el estado
> actual de la aplicación, no un total acumulado."

> Nota para el presentador: el valor baja a 0 cuando el *servidor* termina de procesar
> la solicitud (2 segundos después de recibirla), no cuando alguien cierra la pestaña.
> Dejar las pestañas abiertas no mantiene nada "en progreso" — la solicitud ya terminó
> en cuanto el servidor envió la respuesta. Si alguien del público pregunta por qué
> vuelve a 0 aunque no cerraron nada, esa es la explicación.

## Troubleshooting

**Docker Desktop no está ejecutándose**
Ábrelo desde el menú de inicio y espera a que el ícono de la barra de tareas indique
que está listo antes de correr `docker compose`.

**`docker` no se reconoce como comando**
Docker Desktop no está instalado o no se agregó al PATH. Reinstala Docker Desktop y
reinicia PowerShell (o la sesión de Windows).

**El puerto 8000 ya está ocupado**
Otro proceso lo está usando. Opciones:
- Cierra el proceso que ocupa el puerto.
- O cambia el mapeo en `docker-compose.yml`, por ejemplo `"8080:8000"`, y accede por
  `http://localhost:8080/`.

**El puerto 9090 ya está ocupado**
Igual que arriba, pero para Prometheus: cambia `"9091:9090"` si es necesario.

**La aplicación no responde**
```powershell
docker compose ps
docker compose logs app
```
Revisa si el contenedor `app` está corriendo y si hay errores en el log (por ejemplo,
un error de sintaxis en `app.py`).

**Prometheus no puede conectarse a la aplicación / el target aparece como DOWN**
- Verifica que `prometheus/prometheus.yml` usa `app:8000` (el nombre del servicio),
  no `localhost:8000`.
- Verifica que el contenedor `app` está corriendo (`docker compose ps`).
- Revisa los logs de Prometheus: `docker compose logs prometheus`.

**La métrica no aparece en `/metrics` o en Prometheus**
- Asegúrate de haber visitado `http://localhost:8000/` al menos una vez (la métrica
  se registra pero su valor inicial puede no ser visible hasta el primer request,
  dependiendo de la versión de la librería).
- Espera unos segundos: Prometheus solo actualiza cada `scrape_interval` (5s en este demo).

**Cambié el código y los cambios no aparecen**
Necesitas reconstruir la imagen de la app:
```powershell
docker compose up --build
```
o específicamente:
```powershell
docker compose build app
docker compose up -d
```

**Cómo reconstruir todo desde cero**
```powershell
docker compose down
docker compose up --build
```

**Cómo ver los logs de cada servicio**
```powershell
docker compose logs app
docker compose logs prometheus
docker compose logs -f app   # en vivo (-f = follow)
```

**Ver el estado de los contenedores**
```powershell
docker compose ps
```

## Lo que debería quedar claro al final de la charla

1. Una aplicación puede producir métricas.
2. Una métrica representa algo que ocurre en la aplicación (una solicitud recibida, cuántas se están procesando ahora mismo, etc.).
3. Prometheus puede recolectar esas métricas.
4. Prometheus usa normalmente un modelo *Pull*: pregunta activamente por los datos.
5. Prometheus almacena los valores a lo largo del tiempo (series temporales).
6. PromQL permite hacer preguntas sobre esas métricas.
7. Docker es solo el entorno donde ejecutamos la app y Prometheus — no es el tema de la charla.
