from flask import Flask, render_template, request, redirect, url_for
import subprocess
import time

app = Flask(__name__)

class WiFiManager:
    def __init__(self):
        self.ssid_list = []

    def scan_wifi(self):
        print("Wi-Fiスキャンを開始します...")
        result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
        self.ssid_list = list(filter(None, result.stdout.strip().split("\n")))
        print("スキャンしたSSID:", self.ssid_list)
        return self.ssid_list

wifi_manager = WiFiManager()

# ホットスポットのON/OFF制御
def control_hotspot(action):
    print(f"ホットスポットの状態を {action} します...")  # 現在のアクションを表示
    result = subprocess.run(["nmcli", "con", "show", "--active"], capture_output=True, text=True)
    print("現在の接続状態:", result.stdout)

    if "Jetson" not in result.stdout and action == "off":
        print("ホットスポットはすでにオフです。")
        return

    if action == "on":
        subprocess.run(["sudo", "nmcli", "con", "up", "Jetson"], check=True)
        print("ホットスポットをONにしました。")
    elif action == "off":
        subprocess.run(["sudo", "nmcli", "con", "down", "Jetson"], check=True)
        print("ホットスポットをOFFにしました。")

def connect_to_wifi(ssid, password):
    """
    指定されたSSIDとパスワードでWi-Fiに接続します。
    """
    try:
        print(f"Wi-Fiに接続を試みています: SSID={ssid}, パスワード={password}")

        # Wi-Fi接続コマンドを実行
        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
            capture_output=True,
            text=True
        )

        # コマンド実行結果を出力
        print("nmcliコマンドの出力:", result.stdout)
        print("nmcliコマンドのエラー:", result.stderr)

        # 接続成功の判定
        if result.returncode == 0:
            print("Wi-Fi接続に成功しました。")
            return True
        else:
            print("Wi-Fi接続に失敗しました。")
            return False
    except Exception as e:
        print(f"Wi-Fi接続中にエラーが発生しました: {e}")
        return False

@app.route("/")
def index():
    print("インデックスページが呼ばれました。")
    ssid_list = wifi_manager.ssid_list
    return render_template("index.html", ssids=ssid_list)

@app.route("/connect", methods=["POST"])
def connect():
    ssid = request.form["ssid"]
    password = request.form["password"]
    print(f"接続を試みるSSID: {ssid}, パスワード: {password}")
    control_hotspot("off")
    time.sleep(2)

    if connect_to_wifi(ssid, password):
        print("Wi-Fi接続に成功しました！")
        return "Wi-Fi接続に成功しました！"
    else:
        print("Wi-Fi接続に失敗しました。APモードに戻ります。")
        control_hotspot("on")
        return redirect(url_for("error"))

@app.route("/error")
def error():
    return "Wi-Fi接続に失敗しました。再度試してください。"

if __name__ == "__main__":
    print("アプリケーションが起動しました...")
    wifi_manager.scan_wifi()
    print("Flaskサーバーが起動しました。ポート8080でアクセス可能です。")
    control_hotspot("on")
    app.run(host="0.0.0.0", port=8080)
