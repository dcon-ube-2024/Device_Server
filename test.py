import requests
import json
import time

url = "http://192.168.1.14:3001/api/push"

now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
data_json = {
    "email": "tarougu75@gmail.com",
    "title": "{} 転倒を検知しました".format(now_time),
    "message": "転倒を検知しました。"
}
files={
    "json" : (None, json.dumps(data_json), "application/json"),
}
response = requests.post(url, files=files)
if response.status_code != 200:
    print("Failed to upload data.")
print("Response:", response.text)
print("Status Code:", response.status_code)

