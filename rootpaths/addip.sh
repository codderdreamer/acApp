#!/bin/bash

INTERFACE="eth1"
STATIC_IP="172.16.0.104/16"
ROUTE="172.16.0.0/16"

# Script'in başladığını loglayın
logger "Script Started"

# Sonsuz döngü
while true; do
    # Arayüz 'up' durumuna geçene kadar sürekli kontrol et
    while [[ $(cat /sys/class/net/$INTERFACE/operstate) != "up" ]]; do
        sleep 1
    done

    # 1 süre bekle
    sleep 6

    # Beklemeden sonra arayüzün hala 'up' olup olmadığını kontrol et
    if [[ $(cat /sys/class/net/$INTERFACE/operstate) == "up" ]]; then
        # Statik IP zaten atanmış mı kontrol et
        if ! ip addr show $INTERFACE | grep -q "$STATIC_IP"; then
            # Statik IP'yi noprefixroute ile ekle
            ip addr add $STATIC_IP dev $INTERFACE noprefixroute
            logger "Static IP $STATIC_IP added to $INTERFACE with noprefixroute after delay"
        else
            logger "Static IP $STATIC_IP already exists on $INTERFACE"
        fi

        # Rota zaten var mı kontrol et, yoksa ekle
        if ! ip route show | grep -q "$ROUTE"; then
            ip route add $ROUTE dev $INTERFACE
            logger "Route $ROUTE added for $INTERFACE"
        else
            logger "Route $ROUTE already exists for $INTERFACE"
        fi
    else
        logger "$INTERFACE went down during delay, no IP or route added"
    fi

    # Bir sonraki kontrol öncesi kısa bir süre bekle
    sleep 10
done

