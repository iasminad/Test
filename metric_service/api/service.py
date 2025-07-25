from flask import Flask, jsonify, request, render_template
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

latest_data = []

cpu_gauge = Gauge('system_cpu_usage', 'CPU')
virtual_memory_gauge = Gauge('system_virtual_memory', 'Virtual Memory')
used_ram_gauge = Gauge('system_used_ram', 'Used RAM')
memory_left_gauge = Gauge('system_memory_left', 'Memory Left')


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route("/receive", methods=['POST'])
def receive():
    # global latest_data
    data = request.get_json()
    latest_data.append(data)
    return jsonify(data)


@app.route("/show", methods=['GET'])
def show_data():
    if latest_data:
        return jsonify({"Data": latest_data})
    else:
        return jsonify({"message": "No data received yet"})


@app.route('/metrics')
def metrics():
    if latest_data:
        latest = latest_data[-1]
        cpu_gauge.set(latest.get("CPU", 0))
        virtual_memory_gauge.set(latest.get("Virtual Memory", 0))
        used_ram_gauge.set(latest.get("Used RAM", 0))
        memory_left_gauge.set(latest.get("Memory Left", 0))

    # return Response(generate_latest(), content_type='CONTENT_TYPE_LATEST')
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
