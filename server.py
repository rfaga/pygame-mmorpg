#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket, time, random, string
import thread, string, cPickle
from pygame.event import Event
import serverparser as parser

HOST = ''              # Endereco IP do Servidor
PORT = 5000         # Porta que o Servidor esta

QUIT = 1
MSGTIME = 0.2

#enviador de mensagens - envia mensagens pendentes aos clientes. 
def sendertext():
    while True:
        for client in parser.clients:
            if client.msgbuffer:
                try:
                    client.connection.send(client.msgbuffer.pop(0))
                    print "> Text Msg sent to %s"%client
                except:
                    client.delete()
            else:
                try:
                    client.connection.send("Event(30, {'ping':True}),")
                except:
                    client.close()
        time.sleep(MSGTIME)

#gerenciador de conexoes - espera por conexoes do cliente.
def conn_handler():
    while True:
        #espera pela conexao do cliente. quando chegar, cria um objeto Client e adiciona ao vetor clients
        con, info = tcp.accept()
        client = parser.Client(con, info)
        parser.clients += [client]
        #comeca entao uma thread para ouvir esse cliente
        thread.start_new_thread(connect, tuple([client]))

#gerencia a conexao de um cliente
def connect(client):
    print 'Conectado por', client

    while True:
        try:
            msg = client.recv()
            if not msg:
                continue
            #print client, msg
            client.parse(msg)
        except:
            break

    try:
        print '> Finalizando conexao do cliente', client
        client.delete()
    except:
        pass
    thread.exit()

#tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp = socket.socket()
orig = (HOST, PORT)

tcp.bind(orig)
tcp.listen(1)

thread.start_new_thread(conn_handler, tuple())

thread.start_new_thread(sendertext, tuple())

thread.start_new_thread(parser.monstersmove, tuple())

tcp_root = socket.socket()
orig = ("127.0.0.1", 66666)
tcp_root.bind(orig)
tcp_root.listen(1)

con, info = tcp_root.accept()

####### Interpretador de comandos
command = "nothing"
while command[0] != "quit":
    command = con.recv(1024*1024).split()
    if len(command) == 0: command = "nothing"
    try:
        if command[0] == "send":
            cl = parser.clients[int(command[1])]
            cl.send(string.join(command[2:]))
            con.send("> Message '%s' sent!"%command[2:])
        if command[0] == "sendmsg":
            cl = parser.clients[int(command[1])]
            cl.sendmsg(string.join(command[2:]))
            con.send("> Message '%s' sent!"%command[2:])
        elif command[0] == "ls":
            try:
               for i in range(len(parser.clients)):
                   con.send("> Client %3d: %s"%(i, parser.clients[i]))
            except:
                con.send("no one connected")
        elif command[0] == "kill":
            cl = parser.clients[int(command[1])]
            cl.kill()
        elif command[0] == "kick":
            cl = parser.clients[int(command[1])]
            cl.close()
        elif command[0] == "delete":
            cl = parser.clients[int(command[1])]
            cl.delete()
        elif command[0] == "spawn":
            obj, pos = int(command[1]), eval(command[2])
            parser.addobj(obj, pos)
        elif command[0] == "spawnall":
            parser.monster_spawner(int(command[1]))
        elif command[0] == "e":
            exec(string.join(command[1:]))
        elif command[0] == "help":
            con.send( """
            send n Msg... - envia para o cliente dado de forma crua (sem evento)
            sendmsg n Msg... - envia por evento
            ls - lista os clientes
            kill n - mata o cliente n
            kick n - kicka o cliente n
            spawn obj_code position - cria um objeto do codigo dado na posicao dada em lista [x,y]
            spawnall n: cria diversos monstros randomicamente
            e Codigo: executa o codigo como em python
            """)
        else:
            con.send( "> Ahn??")
        
    except:
        con.send("operation couldn't done")
    #print command

#this is the end
print "> finish"
tcp.close()
