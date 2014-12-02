#!/bin/bash
port="50505"
rm -f /tmp/input; mkfifo /tmp/input; exec 3<> /tmp/input
rm -f /tmp/output; mkfifo /tmp/output; exec 3<> /tmp/output
while true
do
    echo "Start server on port: $port"
    cat /tmp/output | nc -l -p $port >/tmp/input &

    request=()
    count=0
    while read line </tmp/input; do
        #echo "$count $line" | cat -v
        request[$count]=$line
        count=$((count+1))
        if [[ "$line" == `echo -e "\r\n"` || "$line" == `echo -e "\n"` ]];then
            break
        fi
    done

#    echo "Request items and indexes:"
#    for index in ${!request[*]}
#    do
#        echo "$index ${request[$index]}"
#    done

    echo "Request: ${request[0]}"
    Body=""
    if [[ "${request[0]}" =~ "/hello" ]]; then
        Body="<html><h1>Hello world</h></html>"
    fi
    if [[ "${request[0]}" =~ "/echo" ]]; then
        Body=${request[@]}
    fi

    if [[ "${request[0]}" =~ "HTTP" ]]; then
        echo -en "HTTP/1.0 200 OK\nContent-Type: text/html\nContent-Length: ${#Body}\n\n$Body" > /tmp/output;
    else
        echo -en "$Body" > /tmp/output;
    fi
    killall -q nc
    killall -q cat
done