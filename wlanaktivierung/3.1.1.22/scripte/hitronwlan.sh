#!/bin/sh
HOST=192.168.0.1
USER=admin
PASS=password
curl --cookie-jar cookies.txt http://$HOST/login.asp -s
curl --cookie cookies.txt --cookie-jar cookies.txt --data "user=$USER&pws=$PASS" http://$HOST/goform/login -s
curl --cookie cookies.txt --cookie-jar cookies.txt --data "dir=admin/&file=wireless&wireless=1" http://$HOST/goform/Wls -s
curl --cookie cookies.txt http://$HOST/goform/logout -s
