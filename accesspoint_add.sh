#!/bin/sh
echo "WiFi AP oluşturuluyor: $1"
nmcli con add type wifi ifname wlan0 mode ap con-name $1 ssid $1 && \
nmcli con modify $1 802-11-wireless.band bg && \
nmcli con modify $1 802-11-wireless.channel 1 && \
nmcli con modify $1 802-11-wireless-security.key-mgmt wpa-psk && \
nmcli con modify $1 802-11-wireless-security.proto rsn && \
nmcli con modify $1 802-11-wireless-security.group ccmp && \
nmcli con modify $1 802-11-wireless-security.pairwise ccmp && \
nmcli con modify $1 802-11-wireless-security.psk $2 && \
nmcli con modify "$1" ipv4.method shared && \
nmcli con up "$1"
if [ "$3" == "False" ]; then
    nmcli con modify "$1" ipv4.method manual
    nmcli con modify "$1" ipv4.addresses "$4/$5"
    nmcli con modify "$1" ipv4.gateway "$6"
else
    nmcli con modify "$1" ipv4.method shared
fi
nmcli con up "$1"
