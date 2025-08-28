#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>  // 📌 Include JSON library

#define PIEZO_PIN 34  // Analog input pin for piezo sensor

// Wi-Fi Credentials
const char* ssid = "Aranya";         // 🔹 Replace with your Wi-Fi SSID
const char* password = "Aranya543nm"; // 🔹 Replace with your Wi-Fi Password

// Initialize Web Server on port 80
WebServer server(80);

// Thresholds
int heartThreshold = 240;  // Adjust based on sensor sensitivity for heartbeats
int breathThreshold = 100; // Lower threshold for respiration detection

// Heart Rate Variables
unsigned long lastBeatTime = 0;
float bpm = 0;
bool pulseDetected = false;

// Respiration Rate Variables
unsigned long lastBreathTime = 0;
float rr = 0;
bool inhaleDetected = false;

// HRV & Stress Variables
float rrIntervals[10];  // Stores last 10 RR intervals
int rrIndex = 0;
float rmssd = 0;
float stressLevel = 0;

// Fatigue Index Variables
unsigned long startTime, recoveryTime;
bool startFlag = false;
float initialHR = 0, recoveryHR = 0, FI = 0;

// Function to read sensor and compute values
void readSensorData() {
    int sensorValue = analogRead(PIEZO_PIN);

    // ---- HEART RATE (BPM) DETECTION ----
    if (sensorValue > heartThreshold && !pulseDetected) {
        unsigned long currentTime = millis();
        if (currentTime - lastBeatTime > 600) {  
            float rrInterval = (currentTime - lastBeatTime) / 1000.0;
            bpm = 60.0 / rrInterval;
            if (bpm > 40 && bpm < 180) {
                rrIntervals[rrIndex] = rrInterval;
                rrIndex = (rrIndex + 1) % 10;
            }
            lastBeatTime = currentTime;
            pulseDetected = true;
        }
    } else if (sensorValue < (heartThreshold - 30)) {
        pulseDetected = false;
    }

    // ---- RESPIRATION RATE (RR) DETECTION ----
    if (sensorValue > breathThreshold && !inhaleDetected) {
        unsigned long currentTime = millis();
        if (currentTime - lastBreathTime > 3000) {  
            rr = 60.0 / ((currentTime - lastBreathTime) / 1000.0);
            if (rr > 8 && rr < 30) {}
            lastBreathTime = currentTime;
            inhaleDetected = true;
        }
    } else if (sensorValue < (breathThreshold - 20)) {
        inhaleDetected = false;
    }

    // ---- FATIGUE INDEX (FI) CALCULATION ----
    if (!startFlag && bpm > 80) {
        initialHR = bpm;
        startTime = millis();
        startFlag = true;
    }
    if (startFlag && millis() - startTime >= 30000) {  
        recoveryHR = bpm;
        recoveryTime = (millis() - startTime) / 1000;
        FI = (initialHR - recoveryHR) / recoveryTime;
        startFlag = false;
    }

    // ---- HRV (RMSSD) & STRESS LEVEL CALCULATION ----
    if (rrIndex >= 9) {
        float sumSquaredDiffs = 0;
        for (int i = 0; i < 9; i++) {
            float diff = rrIntervals[i + 1] - rrIntervals[i];
            sumSquaredDiffs += diff * diff;
        }
        rmssd = sqrt(sumSquaredDiffs / 9.0);
        stressLevel = map(rmssd * 1000, 10, 150, 100, 0);
        stressLevel = constrain(stressLevel, 0, 100);
    }

    // ---- PRINT VALUES TO SERIAL MONITOR ----
    Serial.print("BPM: "); Serial.print(bpm);
    Serial.print(", RR: "); Serial.print(rr);
    Serial.print(", FI: "); Serial.print(FI);
    Serial.print(", Stress Level: "); Serial.println(stressLevel);
}

// ✅ **Web Server Handler to Send JSON Data**
void handleRoot() {
    readSensorData();

    // Create JSON response
    StaticJsonDocument<200> jsonDoc;
    jsonDoc["Heart Rate"] = String(bpm) + " BPM";
    jsonDoc["Respiration Rate"] = String(rr) + " BPM";
    jsonDoc["Fatigue Index"] = FI;
    jsonDoc["Stress Level"] = stressLevel;

    String jsonResponse;
    serializeJson(jsonDoc, jsonResponse);

    server.sendHeader("Access-Control-Allow-Origin", "*");  // Allow cross-origin access
    server.send(200, "application/json", jsonResponse);  // ✅ Send proper JSON
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }

    Serial.println("\nWi-Fi connected!");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());

    // Start Web Server
    server.on("/", handleRoot);
    server.begin();
}

void loop() {
    readSensorData();  // Read sensor data and update values
    server.handleClient();  // Handle web requests
    delay(100);  // Update every 100ms for faster response
}
