from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
app.config['DEBUG'] = True  # Enable debug mode

INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "1kWhejX1FGCKDYPyerc26Pex2_xGbH_kxHLHgjxmC_1nt5reBsmfK4uaZ5muhjkSb5dm2qmKlUYrlWFx4ntIJw=="
INFLUXDB_ORG = "184fa17bc689338c"
INFLUXDB_BUCKET = "lpr"

@app.route('/query', methods=['GET'])
def query_influxdb():
    query = '''
    from(bucket: "lpr")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "your_measurement")
    '''

    headers = {
        "Authorization": f"Token {INFLUXDB_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "query": query,
        "type": "flux",
        "org": INFLUXDB_ORG
    }

    try:
        response = requests.post(f"{INFLUXDB_URL}/api/v2/query", headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
