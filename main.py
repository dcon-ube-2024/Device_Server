from flask import Flask, render_template, request, redirect, url_for
import subprocess
import time
from enum import Enum

app = Flask(__name__)

class WiFiManager:
    class LanMode(Enum):
        APMode = 1  # Access Point mode
        WifiMode = 2  # Wi-Fi mode

    def __init__(self):
        self.ssid_list = []  # List of SSIDs found during scanning
        self.wifi_mode = self.LanMode.WifiMode  # Default mode is Wi-Fi

    def scan_wifi(self):
        print("Starting Wi-Fi scan...")
        self.wifi_mode = WiFiManager.LanMode.APMode  # Switch to AP mode during scanning
        result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
        self.ssid_list = list(filter(None, result.stdout.strip().split("\n")))  # Filter and store SSIDs
        print("Scanned SSIDs:", self.ssid_list)
        return self.ssid_list

wifi_manager = WiFiManager()

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
        wifi_manager.wifi_mode = WiFiManager.LanMode.APMode
        subprocess.run(["sudo", "nmcli", "con", "up", "Jetson"], check=True)
        print("Hotspot turned ON.")
    elif action == "off":
        wifi_manager.wifi_mode = WiFiManager.LanMode.WifiMode
        subprocess.run(["sudo", "nmcli", "con", "down", "Jetson"], check=True)
        print("Hotspot turned OFF.")

def connect_to_wifi(ssid, password):
    """
    Attempts to connect to a specified Wi-Fi network using the provided SSID and password.
    """
    try:
        print(f"Attempting to connect to Wi-Fi: SSID={ssid}, Password={password}")
        wifi_manager.wifi_mode = WiFiManager.LanMode.WifiMode  # Switch to Wi-Fi mode for connection
        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
            capture_output=True,
            text=True
        )

        print("nmcli command output:", result.stdout)
        print("nmcli command error:", result.stderr)

        if result.returncode == 0:
            wifi_manager.wifi_mode = WiFiManager.LanMode.WifiMode
            print("Successfully connected to Wi-Fi.")
            return True
        else:
            wifi_manager.wifi_mode = WiFiManager.LanMode.APMode
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
    print("Index page accessed.")
    ssid_list = wifi_manager.ssid_list
    return render_template("index.html", ssids=ssid_list)

@app.route("/connect", methods=["POST"])
def connect():
    """
    Handles the connection attempt when a Wi-Fi network is selected.
    """
    ssid = request.form["ssid"]
    password = request.form["password"]
    print(f"Attempting to connect to SSID: {ssid}, Password: {password}")
    control_hotspot("off")  # Turn off hotspot before connecting
    time.sleep(2)

    if connect_to_wifi(ssid, password):
        print("Wi-Fi connection successful!")
        return "Successfully connected to Wi-Fi!"
    else:
        print("Failed to connect to Wi-Fi. Switching back to AP mode.")
        control_hotspot("on")  # Turn hotspot back on in case of failure
        return redirect(url_for("error"))

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
    print("Flask server started. Accessible on port 8080.")
    control_hotspot("on")  # Start the hotspot initially
    app.run(host="0.0.0.0", port=8080)
