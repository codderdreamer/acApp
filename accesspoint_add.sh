#!/bin/sh
echo "WiFi AP oluşturuluyor: $1"
nmcli con add type wifi ifname wlan0 mode ap con-name $1 ssid $1 && \
nmcli con modify $1 802-11-wireless.band bg && \
nmcli con modify $1 802-11-wireless.channel 1 && \
nmcli con modify $1 802-11-wireless-security.key-mgmt wpa-psk && \
nmcli con modify $1 802-11-wireless-security.proto rsn && \
nmcli con modify $1 802-11-wireless-security.group ccmp && \
nmcli con modify $1 802-11-wireless-security.pairwise ccmp && \
nmcli con modify $1 802-11-wireless-security.psk $2 
echo "$3"
if [ "$3" = "True" ]; then
    echo "ipv4.method manual"
    nmcli con modify "$1" ipv4.method manual
    echo "ipv4.addresses"
    nmcli con modify "$1" ipv4.addresses "192.168.1.100/24"
    echo "ipv4.gateway"
    nmcli con modify "$1" ipv4.gateway "192.168.1.1"
else
    nmcli con modify "$1" ipv4.method shared
fi

nmcli con up "$1"
