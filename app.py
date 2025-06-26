from flask import Flask, render_template, request
import math
from utils.calculations import calculate_irrigation_design
from utils.elevation import get_elevation_profile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/calculate', methods=['POST'])
def calculate():
    import json
    from utils.calculations import calculate_irrigation_design
    from utils.elevation import get_elevation_profile

    geojson = request.form.get('geojson')
    crop = request.form.get('crop')
    soil = request.form.get('soil')
    material = request.form.get('material')
    irrigation_type = request.form.get('irrigation')
    pipe_length = float(request.form.get('length', 0))
    duration = float(request.form.get('duration', 0))
    water = float(request.form.get('water', 0))

    # Parse elevation
    polygon = json.loads(geojson)
    elev_min, elev_max = get_elevation_profile(polygon)
    static_head = elev_max - elev_min

    # Compute irrigation result
    result = calculate_irrigation_design(
        crop, soil, material, irrigation_type,
        water, static_head, pipe_length, duration,
        elev_min, elev_max
    )

    return render_template("result.html", result=result)

@app.route('/power')
def power():
    return render_template("power.html")

@app.route('/power_result', methods=['POST'])
def power_result():
    power_kw = float(request.form['power_kw'])
    voltage = float(request.form['voltage'])
    distance = float(request.form['distance'])
    material = request.form['material']
    phase = request.form['phase']

    efficiency = 0.85  # assumed motor efficiency
    pf = 0.85  # assumed power factor

    if phase == 'single':
        current = (1000 * power_kw) / (voltage * efficiency)
    else:
        current = (1000 * power_kw) / (math.sqrt(3) * voltage * efficiency * pf)

    resistivity = 0.017 if material == 'copper' else 0.028  # ohm·mm²/m
    area_mm2 = 10  # default wire size
    resistance = resistivity * (2 * distance) / area_mm2
    v_drop = current * resistance
    percent_drop = (v_drop / voltage) * 100

    return f"Pump Power: {power_kw} kW<br>Phase: {phase.capitalize()}<br>Calculated Current: {current:.2f} A<br>Voltage Drop: {v_drop:.2f} V ({percent_drop:.1f}% of {voltage} V)"


@app.route('/reference')
def reference():
    return render_template("reference.html")


if __name__ == '__main__':
    app.run(debug=True)
