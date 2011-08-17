#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import socket, thread


def receiver():
    while True:
        msg = conn.recv(1024*1024)
        if msg != "":
            print msg

DESTINY = ("127.0.0.1", 66666)
conn = socket.socket()
#conectando com o destino
conn.connect(DESTINY)

thread.start_new_thread(receiver, tuple())

command = ""
while command != "quit":
    command = raw_input()
    if len(command) > 0:
        conn.send(command)
