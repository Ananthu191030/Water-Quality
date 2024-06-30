from flask import Flask, request, jsonify

from flask_cors import CORS

import requests


app = Flask(__name__)

CORS(app)


# Replace with your IBM Cloud API Key

API_KEY = "cpd-apikey-IBMid-693000FZZ0-2024-06-30T10:18:49Z"


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
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():

    try:

        # Extract and convert form data

        data = {

            "temp": float(request.form['temp']),

            "do": float(request.form['do']),

            "ph": float(request.form['ph']),

            "conductivity": float(request.form['conductivity']),

            "bod": float(request.form['bod']),

            "nitrate": float(request.form['nitrate']),

            "fecal_coliform": float(request.form['fecal_coliform']),

            "total_coliform": float(request.form['total_coliform'])

        }


        # Get IAM token

        mltoken = get_iam_token(API_KEY)


        # Prepare payload

        payload_scoring = {

            "input_data": [{

                "fields": ["temp", "do", "ph", "conductivity", "bod", "nitrate", "fecal_coliform", "total_coliform"],

                "values": [list(data.values())]

            }]

        }


        # IBM Cloud endpoint

        url = 'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/771c789b-ad55-4538-8cae-6947296757f4/predictions?version=2021-05-01'

        # Make request to IBM Cloud

        response = requests.post(url, json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
        response.raise_for_status()


        # Process response
        return jsonify(response.json())


    except Exception as e:

        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':

    app.run(debug=True)

