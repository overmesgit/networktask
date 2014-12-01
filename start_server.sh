#!/bin/bash
port="50505"
rm -f /tmp/input; mkfifo /tmp/input; exec 3<> /tmp/input
rm -f /tmp/output; mkfifo /tmp/output; exec 3<> /tmp/output
echo "start checker"
while true
do
    res=`ss -ntl | grep -c "$port"`
    echo $res
    if [ $res -eq 0 ]; then
        echo "start server"
        cat /tmp/output | nc -l -p $port >/tmp/input &
    fi
    if read line </tmp/input; then
        echo $line
        if [[ "$line" =~ "/hello" ]]; then
            echo "sometext" > /tmp/output;
        fi
        if [[ "$line" =~ "/echo" ]]; then
            echo "$line" > /tmp/output;
        fi
    fi
done