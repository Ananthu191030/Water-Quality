from flask import Flask, request, jsonify, render_template,json
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_cors import CORS
import requests
import logging
from forms import PredictForm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)
CORS(app)

app.secret_key = 'fdbc4b27-47ef-4510-bc93-d7198a2b212a'  # You will need a secret key

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
                "D.O.": float(form.DO.data),
                "PH": float(form.PH.data),
                "CONDUCTIVITY": float(form.CONDUCTIVITY.data),
                "B.O.D.": float(form.BOD.data),
                "NITRATENAN": float(form.NITRATE_NITRITE.data),
                "FECAL COLIFORM": float(form.FECAL_COLIFORM.data),
                "TOTAL COLIFORM": float(form.TOTAL_COLIFORM.data)
            }
            userInput=[]
            userInput.append(data)

            logging.debug(f"Form data: {data}")

            # Get IAM token
            mltoken = get_iam_token(API_KEY)
            logging.debug(f"IAM token: {mltoken}")

            # Prepare payload for IBM Cloud
            payload_scoring = {
                "input_data": [
                    {
                        "fields": [ 
                            "STATE", "Temp", "D.O.", "PH", "CONDUCTIVITY",
                            "B.O.D.", "NITRATENAN",
                            "FECAL COLIFORM", "TOTAL COLIFORM"
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
            url = 'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/fdbc4b27-47ef-4510-bc93-d7198a2b212a/predictions?version=2021-05-01'

            # Create session with retry logic
            session = create_session()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + mltoken
            }
            
            # Adjust timeout as needed (connect_timeout, read_timeout)
            response = requests.post( url, json=payload_scoring, headers=headers, timeout=(5, 30))
            response.raise_for_status()

            logging.debug(f"Response: {response.json()}")

            # Process response and return prediction as JSON
            output = response.json()
            #output=json.loads(response.txt)
            print(output)

    # Check if 'predictions' key exists in output
            if 'predictions' in output and output['predictions']:
                 prediction_value = output['predictions'][0]['values'][0][0]
                 rounded_prediction = round(prediction_value, 2)

        # Assign the prediction result to form attribute for display
                 form.result =  rounded_prediction
                 return jsonify({'quality': rounded_prediction})
                 return render_template('index.html', form=form)
            else:
                  error_message = "No predictions found in the response."
                  print(error_message)
                  return render_template('index.html', form=form, error=error_message)

        except requests.exceptions.RequestException as e:
         error_message = f"Error fetching prediction: {e}"
         print(error_message)
         return render_template('index.html', form=form, error=error_message)
if __name__ == "__main__":
    app.run(debug=True)
