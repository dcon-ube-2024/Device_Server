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

## Jetson mDNS
1. avahi-deamon のインストール
```
sudo apt-get install avahi-daemon
```
2. ホストネームの変更
/etc/hostname  
```
jetson 
```
/etc/hosts
```
127.0.0.1       localhost
127.0.1.1       jetson

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```
3. 再起動
```
reboot
```

これで `{ユーザー名}@jetson `で他デバイスからアクセス可能