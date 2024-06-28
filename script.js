const API_KEY = "iBkuz5ZjS4RMQ_Uk4kzONaJ6t9r2FmN5NFTo7Ydx0z7h";

function getToken(errorCallback, loadCallback) {
  const req = new XMLHttpRequest();
  req.addEventListener("load", loadCallback);
  req.addEventListener("error", errorCallback);
  req.open("POST", "https://iam.cloud.ibm.com/identity/token");
  req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  req.setRequestHeader("Accept", "application/json");
  req.send("grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=" + API_KEY);
}

function apiPost(scoring_url, token, payload, loadCallback, errorCallback){
  const oReq = new XMLHttpRequest();
  oReq.addEventListener("load", loadCallback);
  oReq.addEventListener("error", errorCallback);
  oReq.open("POST", scoring_url);
  oReq.setRequestHeader("Accept", "application/json");
  oReq.setRequestHeader("Authorization", "Bearer " + token);
  oReq.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  oReq.send(payload);
}

function calculateWaterQuality() {
  const state = document.getElementById('state').value;
  const temp = parseFloat(document.getElementById('temp').value);
  const doValue = parseFloat(document.getElementById('do').value);
  const ph = parseFloat(document.getElementById('ph').value);
  const conductivity = parseFloat(document.getElementById('conductivity').value);
  const bod = parseFloat(document.getElementById('bod').value);
  const nitrate = parseFloat(document.getElementById('nitrate').value);
  const fecalColiform = parseFloat(document.getElementById('fecal_coliform').value);
  const totalColiform = parseFloat(document.getElementById('total_coliform').value);

  const values = [[state, temp, doValue, ph, conductivity, bod, nitrate, fecalColiform, totalColiform]];
  const payload = JSON.stringify({ input_data: [{ fields: ["state", "temp", "do", "ph", "conductivity", "bod", "nitrate", "fecal_coliform", "total_coliform"], values }] });

  getToken(
    (err) => console.log(err),
    function () {
      let tokenResponse;
      try {
        tokenResponse = JSON.parse(this.responseText);
      } catch (ex) {
        console.error("Failed to parse token response", ex);
        return;
      }

      const scoring_url = "https://private.us-south.ml.cloud.ibm.com/ml/v4/deployments/010cb094-8d7e-4ecb-bb1e-f74dc26fb228/predictions?version=2021-05-01";
      apiPost(scoring_url, tokenResponse.access_token, payload, function (resp) {
        let parsedPostResponse;
        try {
          parsedPostResponse = JSON.parse(this.responseText);
        } catch (ex) {
          console.error("Failed to parse scoring response", ex);
          return;
        }

        const quality = parsedPostResponse.predictions[0].values[0][0];
        const qualityResult = document.getElementById('qualityResult');
        let qualityText;

        switch (quality) {
          case 5:
            qualityText = "Excellent Quality";
            break;
          case 4:
            qualityText = "Good Quality";
            break;
          case 3:
            qualityText = "Fair Quality";
            break;
          case 2:
            qualityText = "Poor Quality";
            break;
          case 1:
            qualityText = "Very Poor Quality";
            break;
          default:
            qualityText = "Unknown Quality";
        }

        qualityResult.textContent = `Water Quality: ${qualityText}`;
      }, function (error) {
        console.error("Error during scoring request", error);
      });
    }
  );
}

function loadHomePage() {
  document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}
