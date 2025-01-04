# device_server

## Jetson AP Mode
### 初期設定
1. network-managerのインストール
```
sudo apt update
sudo apt install network-manager
```
2. インターフェース名の確認
```
nmcli device
```
大抵の場合wlan0
3. アクセスポイントの作成
con-nameとssidは変更可能
```
sudo nmcli connection add type wifi ifname wlan0 mode ap con-name MyHotspot ssid Jetson-Hotspot
```
4. セキュリティ設定
"password"は変更可能
```
sudo nmcli connection modify MyHotspot 802-11-wireless.band bg
sudo nmcli connection modify MyHotspot 802-11-wireless-security.key-mgmt wpa-psk
sudo nmcli connection modify MyHotspot 802-11-wireless-security.psk "password"
```
### ON/OFF
オフの状態でdownコマンドを打つとエラーが発生する
Jetsonを通常のWi-Fiに接続するときはAPモードをオフにしなければならない
```
sudo nmcli connection up MyHotspot
sudo nmcli connection down MyHotspot
```