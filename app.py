from flask import Flask, request, jsonify, render_template
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_cors import CORS
import requests
import logging
from forms import PredictForm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)
CORS(app)
csrf = CSRFProtect(app)
app.secret_key = 'c6558f3a-8432-435b-8dfb-2db0a145d88b'  # You will need a secret key

# Replace with your IBM Cloud API Key
API_KEY = "qDVtrAXtDMZMnu6s0_35iklKtpLhCnspVT6Gjgfc76Jq"

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        raise
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        raise

# Function to create a session with retry logic
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('https://', adapter)
    return session

@app.route('/', methods=('GET', 'POST'))
def startApp():
    form = PredictForm()
    return render_template('index.html', form=form)

@app.route('/predict', methods=['POST'])
def predict():
    form = PredictForm()
    if form.validate_on_submit():
        try:
            # Extract and convert form data
            data = {
                "STATE": form.STATE.data,
                "Temp": float(form.Temp.data),
                "D.O(mg/l)": float(form.DO.data),
                "PH": float(form.PH.data),
                "CONDUCTIVITY (µhos/cm)": float(form.CONDUCTIVITY.data),
                "B.O.D. (mg/l)": float(form.BOD.data),
                "NITRATENAN N+ NITRITENANN (mg/l)": float(form.NITRATE_NITRITE.data),
                "FECAL COLIFORM (MPN/100ml)": float(form.FECAL_COLIFORM.data),
                "TOTAL COLIFORM (MPN/100ml)Mean": float(form.TOTAL_COLIFORM.data)
            }

            logging.debug(f"Form data: {data}")

            # Get IAM token
            mltoken = get_iam_token(API_KEY)
            logging.debug(f"IAM token: {mltoken}")

            # Prepare payload for IBM Cloud
            payload_scoring = {
                "input_data": [
                    {
                        "fields": [
                            "STATE", "Temp", "D.O(mg/l)", "PH", "CONDUCTIVITY (µhos/cm)",
                            "B.O.D. (mg/l)", "NITRATENAN N+ NITRITENANN (mg/l)",
                            "FECAL COLIFORM (MPN/100ml)", "TOTAL COLIFORM (MPN/100ml)Mean"
                        ],
                        "values": [
                            [
                                form.STATE.data,
                                float(form.Temp.data),
                                float(form.DO.data),
                                float(form.PH.data),
                                float(form.CONDUCTIVITY.data),
                                float(form.BOD.data),
                                float(form.NITRATE_NITRITE.data),
                                float(form.FECAL_COLIFORM.data),
                                float(form.TOTAL_COLIFORM.data)
                            ]
                        ]
                    }
                ]
            }
            logging.debug(f"Payload: {payload_scoring}")

            # IBM Cloud endpoint for model predictions
            url = 'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/c6558f3a-8432-435b-8dfb-2db0a145d88b/predictions?version=2021-05-01'

            # Create session with retry logic
            session = create_session()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + mltoken
            }
            
            # Adjust timeout as needed (connect_timeout, read_timeout)
            response = session.request('POST', url, json=payload_scoring, headers=headers, timeout=(5, 30))
            response.raise_for_status()

            logging.debug(f"Response: {response.json()}")

            # Process response and return prediction as JSON
            output = response.json()
            prediction = output['predictions'][0]['values'][0][0]  # Assuming the prediction is in this format
            form.result = round(prediction, 2)  # Return the result to the form
            return render_template('index.html', form=form)

        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    else:
        # If the form is not valid, render the template with the form again
        return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
