import requests
import json

# ✅ Web Server URL (Modify as per your ESP32 or API)
WEB_SERVER_URL = "http://192.168.141.154/"  # Change this to match your web server

# ✅ Function to Fetch Health Data from Web Server
def fetch_health_data():
    try:
        response = requests.get(WEB_SERVER_URL, timeout=5)  # Fetch data from the web server
        response.raise_for_status()  # Raise an error if the request fails

        try:
            data = response.json()  # ✅ Try parsing JSON response
        except requests.exceptions.JSONDecodeError:
            data = {"error": "Invalid JSON received", "raw_response": response.text}  # Handle non-JSON response
        
        return data
    except requests.RequestException as e:
        return {"error": f"Failed to fetch data from Web Server: {e}"}

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

# ✅ Main Function
def main():
    print("Fetching health data from Web Server...")
    health_data = fetch_health_data()

    # ✅ Check if data is valid JSON
    if not isinstance(health_data, dict):
        print("Error: Received non-JSON data")
        print(f"Raw Response: {health_data}")
        return

    if "error" in health_data:
        print(health_data["error"])
        return

    print("\nHealth Data:")
    for key, value in health_data.items():
        print(f"{key}: {value}")

    print("\nPredicting possible diseases using AI...")
    prediction = predict_disease(health_data)

    print("\nPrediction:")
    print(prediction)

# ✅ Run the Script
if __name__ == "__main__":
    main()
