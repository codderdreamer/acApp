#!/bin/sh
while :
do
    gpio-test.64 w e 18 0 >/dev/null
    sleep 0.5
    gpio-test.64 w e 18 1 >/dev/null
    sleep 0.5
done
