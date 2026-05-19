from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# API KEY
API_KEY = "f43acb00-c80e-456a-bf7d-821f625263d6"

# URLs API
geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"

# --------------------------------
# GEOCODING
# --------------------------------
def geocode(location):

    params = {
        "q": location,
        "limit": 1,
        "key": API_KEY
    }

    response = requests.get(geocode_url, params=params)
    data = response.json()

    if "hits" not in data or len(data["hits"]) == 0:
        return None

    point = data["hits"][0]["point"]

    return point["lng"], point["lat"]

# --------------------------------
# RUTA
# --------------------------------
def route(c1, c2):

    params = {
        "point": [
            f"{c1[1]},{c1[0]}",
            f"{c2[1]},{c2[0]}"
        ],
        "vehicle": "car",
        "key": API_KEY,
        "type": "json"
    }

    response = requests.get(route_url, params=params)
    data = response.json()

    if "paths" not in data:
        return None

    path = data["paths"][0]

    # Distancia en kilómetros
    distance = round(path["distance"] / 1000, 2)

    # Tiempo en milisegundos
    time_ms = path["time"]

    total_seconds = int(time_ms / 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    duration = f"{hours}h {minutes}m {seconds}s"

    # Combustible estimado
    # Promedio: 12 km por litro
    fuel = round(distance / 12, 2)

    return {
        "duration": duration,
        "fuel": fuel
    }

# --------------------------------
# HTML
# --------------------------------
HTML = """
<!DOCTYPE html>
<html lang="es">

<head>

    <meta charset="UTF-8">
    <title>Calculador de Viaje</title>

    <style>

        body{
            font-family: Arial;
            background: #f2f2f2;
            padding: 30px;
        }

        .container{
            width: 500px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px gray;
        }

        input{
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
        }

        button{
            padding: 10px 20px;
            background: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover{
            background: #0056b3;
        }

        .resultado{
            margin-top: 20px;
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
        }

    </style>

</head>

<body>

<div class="container">

    <h2>🚗 Calculador de Viaje</h2>

    <form method="POST">

        <label>Origen:</label>
        <input type="text" name="origen" required>

        <label>Destino:</label>
        <input type="text" name="destino" required>

        <button type="submit">
            Calcular
        </button>

    </form>

    {% if error %}
        <p style="color:red;">
            {{error}}
        </p>
    {% endif %}

    {% if r %}

    <div class="resultado">

        <h3>Resultados del Viaje</h3>

        <p>
            <strong>⏰ Duración:</strong>
            {{r.duration}}
        </p>

        <p>
            <strong>⛽ Combustible requerido:</strong>
            {{r.fuel}} litros
        </p>

    </div>

    <br>

    <form method="POST" action="/shutdown">
        <button type="submit">
            Salir (Q)
        </button>
    </form>

    <p>También puedes presionar la tecla "Q"</p>

    {% endif %}

</div>

<script>

document.addEventListener("keydown", function(e){

    if(e.key.toLowerCase() === "q"){

        fetch("/shutdown", {
            method:"POST"
        })
        .then(() => {
            alert("Servidor cerrado");
        });

    }

});

</script>

</body>
</html>
"""

# --------------------------------
# PÁGINA PRINCIPAL
# --------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    error = None

    if request.method == "POST":

        origin = request.form["origen"]
        destination = request.form["destino"]

        c1 = geocode(origin)
        c2 = geocode(destination)

        if not c1 or not c2:

            error = "No se encontró la ubicación"

        else:

            result = route(c1, c2)

    return render_template_string(
        HTML,
        r=result,
        error=error
    )

# --------------------------------
# APAGAR SERVIDOR
# --------------------------------
@app.route("/shutdown", methods=["POST"])
def shutdown():

    func = request.environ.get("werkzeug.server.shutdown")

    if func:
        func()
        return "Servidor cerrado"

    return "No se pudo cerrar"

# --------------------------------
# EJECUTAR
# --------------------------------
if __name__ == "__main__":
    app.run(debug=True)