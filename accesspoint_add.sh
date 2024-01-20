# #!/bin/sh

nmcli con add type wifi ifname wlan0 mode ap con-name HelperBox ssid HelperBox && \
nmcli con modify HelperBox 802-11-wireless.band bg && \
nmcli con modify HelperBox 802-11-wireless.channel 1 && \
nmcli con modify HelperBox 802-11-wireless-security.key-mgmt wpa-psk && \
nmcli con modify HelperBox 802-11-wireless-security.proto rsn && \
nmcli con modify HelperBox 802-11-wireless-security.group ccmp && \
nmcli con modify HelperBox 802-11-wireless-security.pairwise ccmp && \
nmcli con modify HelperBox 802-11-wireless-security.psk 11223344 && \
nmcli con modify HelperBox ipv4.method shared && \
nmcli con up HelperBox