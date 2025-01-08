import requests
import json
import time  # 時間計測のために追加

# サーバーのURL（エンドポイント）
url = "http://192.168.1.14:3001/api/upload"

# JSONデータを文字列としてパース
json_data = {
    "user_id": "945f9618-3f67-4010-82ff-272afe7f5128",
}

imageFile = "test.txt"
# 画像ファイルをバイナリモードで開く
with open(imageFile, "rb") as f:
    # バイナリデータを読み込む
    image_data = f.read()

# マルチパートフォームデータを作成
files = {
    "json": (None, json.dumps(json_data), "application/json"),
    "file": (imageFile, image_data, "text/plain"),
}

# リクエスト開始時間を計測
start_time = time.time()

# マルチパートフォームでPOSTリクエストを送信
response = requests.post(url, files=files)

# リクエスト終了時間を計測
end_time = time.time()

# 処理時間を計算
elapsed_time = end_time - start_time

# レスポンスを表示
print("Status Code:", response.status_code)
print("Response Body:", response.text)
print(f"Request processing time: {elapsed_time:.4f} seconds")