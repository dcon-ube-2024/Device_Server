from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import time
from enum import Enum
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

class WiFiManager:
    class LanMode(Enum):
        APMode = 1
        WifiMode = 2

    def __init__(self):
        self.ssid_list = []
        self.wifi_mode = self.LanMode.WifiMode

    def scan_wifi(self):
        print("Starting Wi-Fi scan...")
        self.wifi_mode = WiFiManager.LanMode.APMode
        result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
        self.ssid_list = list(filter(None, result.stdout.strip().split("\n")))
        print("Scanned SSIDs:", self.ssid_list)
        return self.ssid_list

wifi_manager = WiFiManager()

BASE_URL = "http://192.168.1.14:3001"

SAVED_WIFI_PATH = "data/saved_wifi.json"

# Helper function to load saved Wi-Fi credentials
def load_saved_wifi():
    """
    Loads saved Wi-Fi credentials from a JSON file.

    Returns:
        dict: A dictionary with saved SSID and password, or None if not found.
    """
    try:
        with open(SAVED_WIFI_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Helper function to save Wi-Fi credentials
def save_wifi_credentials(ssid, password):
    """
    Saves Wi-Fi credentials to a JSON file.

    Args:
        ssid (str): The SSID of the Wi-Fi network.
        password (str): The password of the Wi-Fi network.
    """
    with open(SAVED_WIFI_PATH, "w") as f:
        json.dump({"ssid": ssid, "password": password}, f)

def control_hotspot(action):
    """
    Controls the status of the hotspot based on the action ('on' or 'off').
    """
    print(f"Changing hotspot status to {action}...")
    result = subprocess.run(["nmcli", "con", "show", "--active"], capture_output=True, text=True)
    print("Current connection status:", result.stdout)

    if "Jetson" not in result.stdout and action == "off":
        print("Hotspot is already off.")
        return

    if action == "on":
        wifi_manager.wifi_mode = wifi_manager.LanMode.APMode
        subprocess.run(["sudo", "nmcli", "con", "up", "Jetson"], check=True)
        print("Hotspot turned ON.")
    elif action == "off":
        wifi_manager.wifi_mode = wifi_manager.LanMode.WifiMode
        subprocess.run(["sudo", "nmcli", "con", "down", "Jetson"], check=True)
        print("Hotspot turned OFF.")

def connect_to_wifi(ssid, password):
    """
    Attempts to connect to a specified Wi-Fi network using the provided SSID and password.
    """
    try:
        print(f"Attempting to connect to Wi-Fi: SSID={ssid}, Password={password}")
        wifi_manager.wifi_mode = wifi_manager.LanMode.WifiMode
        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
            capture_output=True,
            text=True
        )

        print("nmcli command output:", result.stdout)
        print("nmcli command error:", result.stderr)

        if result.returncode == 0:
            wifi_manager.wifi_mode = wifi_manager.LanMode.WifiMode
            save_wifi_credentials(ssid, password)
            print("Successfully connected to Wi-Fi.")
            return True
        else:
            wifi_manager.wifi_mode = wifi_manager.LanMode.APMode
            print("Failed to connect to Wi-Fi.")
            return False
    except Exception as e:
        print(f"An error occurred while connecting to Wi-Fi: {e}")
        return False

@app.route("/")
def index():
    """
    Index page route that displays the available SSIDs.
    """
    if(wifi_manager.wifi_mode == wifi_manager.LanMode.WifiMode):
        print("Index page accessed. Wi-Fi mode is active.")
        return render_template("index_w.html")
    if(wifi_manager.wifi_mode == wifi_manager.LanMode.APMode):
        print("Index page accessed. AP mode is active.")
        ssid_list = wifi_manager.ssid_list
        return render_template("index_a.html", ssids=ssid_list)

@app.route("/login", methods=["POST"])
def login():
    mailadress = request.form["email"]
    password = request.form["password"]
    url="{}/api/login_device".format(BASE_URL)
    data = {
        "email": mailadress,
        "password": password
    }
    dataset = {
        "json" : (None, json.dumps(data), "application/json"),
    }
    response = requests.post(url, files=dataset)
    if(response.status_code == 200):
        response_data = response.json()
        user_id = response_data.get("user_id")
        path = 'data/login.json'
        with open(path, 'w') as f:
            json.dump({"email": mailadress, "password": password, "user_id": user_id}, f)
        print("Login successful!")
        return redirect(url_for("index"))
    else:
        print("Login failed.")
        return redirect(url_for("error"))

@app.route("/connect", methods=["POST"])
def connect():
    """
    Handles the connection attempt when a Wi-Fi network is selected.
    """
    ssid = request.form["ssid"]
    password = request.form["password"]
    print(f"Attempting to connect to SSID: {ssid}, Password: {password}")
    control_hotspot("off")
    time.sleep(2)

    if connect_to_wifi(ssid, password):
        print("Wi-Fi connection successful!")
        return "Successfully connected to Wi-Fi!"
    else:
        print("Failed to connect to Wi-Fi. Switching back to AP mode.")
        control_hotspot("on")
        return redirect(url_for("error"))

@app.route("/upload", methods=["POST"])
def upload():
    """
    Handles the file upload request from the web interface.
    """
    login_data = None
    path = 'data/login.json'
    try:
        with open(path, 'r') as f:
            login_data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Please log in first."}), 400

    if 'files' not in request.files:
        print(request.files)
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    user_id_json = json.dumps({"user_id": login_data["user_id"]})
    
    for file in files:
        url = "{}/api/upload".format(BASE_URL)
        files_data = {
            "json": (None, user_id_json, "application/json"),
            "file": (file.filename, file.stream, file.content_type)
        }
        response = requests.post(url, files=files_data)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to upload {file.filename}"}), 500

    return jsonify({"success": "All files uploaded successfully"}), 200

@app.route("/error")
def error():
    """
    Error page route that is shown when Wi-Fi connection fails.
    """
    return "Wi-Fi connection failed. Please try again."


if __name__ == "__main__":
    """
    Main entry point for the Flask application. Starts the app and performs initial Wi-Fi scan.
    """
    print("Application starting...")
    wifi_manager.scan_wifi()
    saved_wifi = load_saved_wifi()
    if saved_wifi:
        print(f"Found saved Wi-Fi credentials. Attempting to connect to SSID: {saved_wifi['ssid']}")
        if connect_to_wifi(saved_wifi["ssid"], saved_wifi["password"]):
            print("Successfully connected to saved Wi-Fi network.")
            control_hotspot("off")
        else:
            print("Failed to connect to saved Wi-Fi network. Switching to AP mode.")
            control_hotspot("on")
    else:
        print("No saved Wi-Fi credentials found. Starting in AP mode.")
        control_hotspot("on")
    print("Flask server started. Accessible on port 8080.")
    app.run(host="0.0.0.0", port=8080)
