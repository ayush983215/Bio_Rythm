from flask import Flask, jsonify
import requests
import json

app = Flask(__name__)

# ✅ Web Server URL (Modify to match your data source)
WEB_SERVER_URL = "http://192.168.141.154/"  # Update this to your actual web server

# ✅ Function to Fetch Health Data from Web Server
def fetch_health_data():
    try:
        response = requests.get(WEB_SERVER_URL, timeout=5)
        response.raise_for_status()
        return response.json()  # ✅ Parse JSON
    except requests.RequestException as e:
        return {"error": f"Failed to fetch data: {e}"}

# ✅ Function to Predict Disease Using Ollama
def predict_disease(health_data):
    url = "http://localhost:11434/api/generate"  # Ollama API Endpoint
    headers = {"Content-Type": "application/json"}

    prompt = f"""
    Analyze the following health data and predict possible diseases:
    {json.dumps(health_data, indent=2)}
    """

    data = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result.get("response", "No response received")
    except requests.RequestException as e:
        return f"Error connecting to Ollama: {e}"

# ✅ API Endpoint to Get Prediction
@app.route('/prediction', methods=['GET'])
def get_prediction():
    health_data = fetch_health_data()

    if "error" in health_data:
        return jsonify({"error": health_data["error"]})

    prediction = predict_disease(health_data)
    return jsonify({"prediction": prediction})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
