from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

IBM_CLOUD_API_KEY = 'MOab8w1Ftt4jgDJuecIpw6rE3a3dR3hzg92IiMFqjBN3'  # Replace with your actual API key
IBM_CLOUD_URL = 'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/water_quality_test/predictions?version=2021-05-01'  # Replace with your actual IBM Cloud model URL

def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        temp = float(request.form.get('temp'))
        do = float(request.form.get('do'))
        ph = float(request.form.get('ph'))
        conductivity = float(request.form.get('conductivity'))
        bod = float(request.form.get('bod'))
        nitrate = float(request.form.get('nitrate'))
        fecal_coliform = float(request.form.get('fecal_coliform'))
        total_coliform = float(request.form.get('total_coliform'))
    except ValueError as e:
        app.logger.error(f"ValueError: {e}")
        return jsonify({'error': 'Invalid input: could not convert to float'}), 400

    data = {
        "input_data": [
            {
                "field": [["temp", "do", "ph", "conductivity", "bod", "nitrate", "fecal_coliform", "total_coliform"]],
                "values": [[temp, do, ph, conductivity, bod, nitrate, fecal_coliform, total_coliform]]
            }
        ]
    }

    try:
        iam_token = get_iam_token(IBM_CLOUD_API_KEY)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {iam_token}'
        }

        response = requests.post(
            IBM_CLOUD_URL,
            json=data,
            headers=headers
        )

        response.raise_for_status()  # Raise an HTTPError for bad responses
        prediction = response.json()
        quality_level = prediction['predictions'][0]['values'][0][0]  # Adjust based on your response format

        return jsonify({'quality': quality_level})
    except requests.exceptions.HTTPError as http_err:
        app.logger.error(f"HTTPError: {http_err}")
        return jsonify({'error': 'Failed to get prediction from IBM Cloud'}), response.status_code
    except Exception as err:
        app.logger.error(f"Error: {err}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
