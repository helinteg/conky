#!/bin/zsh

arr=(2 4 7 9)
echo `nc localhost 7634 | cut -d "|" -f ${arr[1]}`  `nc localhost 7634 | cut -d "|" -f ${arr[2]}`
echo `nc localhost 7634 | cut -d "|" -f ${arr[3]}`  `nc localhost 7634 | cut -d "|" -f ${arr[4]}`
