import cv2
import requests
import tkinter as tk
from ultralytics import YOLO
from PIL import Image, ImageTk
import time

# ✅ ESP32 HTTP Server URL (Replace with your ESP32 IP)
ESP32_HTTP_URL = "http://192.168.141.154/"  # Change this URL as needed

# ✅ Function to read ESP32 sensor data via HTTP
def read_esp32_data():
    try:
        response = requests.get(ESP32_HTTP_URL, timeout=5)
        if response.status_code == 200:
            return response.json()  # Assuming ESP32 returns JSON
    except requests.exceptions.RequestException as e:
        print("Error fetching data from ESP32:", e)
    return {}

# ✅ Load YOLOv8 model
model = YOLO("yolov8n.pt")

# ✅ Open webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Set width
cap.set(4, 1080)  # Set height

# ✅ Initialize Tkinter window
root = tk.Tk()
root.title("Health Monitoring UI")
root.geometry("800x600")

# ✅ Create a label to display the video
video_label = tk.Label(root)
video_label.pack()

# ✅ Create an information card (Initially hidden)
info_frame = tk.Frame(root, bg="white", padx=10, pady=10)
info_frame.place_forget()

# ✅ Labels for sensor data (2x3 grid)
labels = []
for i in range(2):
    for j in range(3):
        lbl = tk.Label(info_frame, text="", bg="white", fg="black", font=("Arial", 12), padx=5, pady=5)
        lbl.grid(row=i, column=j, padx=5, pady=5)
        labels.append(lbl)

# ✅ Global variable to track when the info box was shown
info_box_start_time = None

# ✅ Function to update UI with sensor data
def update_health_data():
    data = read_esp32_data()
    if data:
        keys = list(data.keys())
        for i in range(min(5, len(keys))):
            labels[i].config(text=f"{keys[i]}: {data[keys[i]]}")

# ✅ Function to show the info box for 7 seconds
def on_button_click():
    global info_box_start_time
    update_health_data()
    info_frame.place(x=300, y=100)  # Show info box
    info_box_start_time = time.time()  # Start timer

# ✅ Button to display health data
button = tk.Button(root, text="Info", bg="red", fg="white", command=on_button_click)
button.place(x=100, y=100)

# ✅ Function to process video & detect faces
def process_video():
    global info_box_start_time
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)  # Mirror the webcam feed
    results = model(frame)

    # ✅ If face detected, update button position
    if results and len(results[0].boxes):
        box = results[0].boxes.xyxy[0].tolist()
        x1, y1, x2, y2 = map(int, box)

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Position the button near the detected face
        button_x = x1 + (x2 - x1) // 2 - 20
        button_y = max(y1 - 40, 10)
        button.place(x=button_x, y=button_y)

    # ✅ Hide the info box after 7 seconds
    if info_box_start_time and time.time() - info_box_start_time > 7:
        info_frame.place_forget()
        info_box_start_time = None  # Reset timer

    # ✅ Convert frame to Tkinter format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(10, process_video)  # Repeat video processing

# ✅ Start video processing
process_video()

# ✅ Run Tkinter event loop
root.mainloop()

# ✅ Release resources
cap.release()
cv2.destroyAllWindows()
