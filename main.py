from flask import Flask, jsonify, render_template
import requests
import json
import serial
import time

app = Flask(__name__)

# ✅ Initialize serial connection with ESP32
try:
    esp32 = serial.Serial('COM4', 115200, timeout=1)  # Change COM port accordingly
    time.sleep(2)  # Allow ESP32 to stabilize
except serial.SerialException as e:
    print("Error opening serial port:", e)
    esp32 = None

# ✅ Function to read health data from ESP32
def read_esp32_data():
    if esp32 is None or not esp32.is_open:
        return {"error": "ESP32 not connected"}

    try:
        esp32.write(b'GET_DATA\n')  # Request data from ESP32
        line = esp32.readline().decode('utf-8').strip()
        
        if line:
            values = line.split(',')
            if len(values) == 5:
                health_data = {
                    "Heart Rate": values[0] + " BPM",
                    "Respiration Rate": values[1] + " BPM",
                    "Fatigue Index": values[2],
                    "Stress Level": values[3],
                    "Blood Pressure": values[4]
                }
                return health_data
    except Exception as e:
        print("Error reading from ESP32:", e)
        return {"error": "Could not read data"}
    
    return {"error": "No data received"}

# ✅ Function to predict disease using Ollama
def predict_disease(health_data):
    url = "http://localhost:11434/api/generate"  # Ollama API endpoint
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
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        return result.get("response", "No response received")
    except requests.RequestException as e:
        return f"Error connecting to Ollama: {e}"

# ✅ API endpoint to fetch health data and prediction
@app.route('/')
def home():
    health_data = read_esp32_data()
    
    if "error" in health_data:
        return jsonify(health_data)
    
    prediction = predict_disease(health_data)
    
    return render_template('index.html', health_data=health_data, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
