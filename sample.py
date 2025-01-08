import requests
import json
import time

# サーバーのURL（エンドポイント）
url = "http://localhost:8080/upload"

imageFile1 = "test1.txt"
imageFile2 = "test2.txt"

files = [("files", (imageFile1, open(imageFile1, "rb"), "text/plain")),
         ("files", (imageFile2, open(imageFile2, "rb"), "text/plain"))]

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
print("Elapsed Time:", elapsed_time)