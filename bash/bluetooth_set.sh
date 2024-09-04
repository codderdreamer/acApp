#!/bin/sh

rfkill unblock all

SDIO=`cat /sys/bus/sdio/devices/mmc2*1/device`
if [ $SDIO = "0x0145" ];then
        killall hciattach
        hciattach -n -s 1500000 /dev/ttyS1 sprd &
elif [ $SDIO = "0xc821" ];then
        killall rtk_hciattach
        rtk_hciattach -n -s 115200 /dev/ttyS1 rtk_h5 &
fi

hciconfig hci0 up && hciconfig hci0 piscan & exit