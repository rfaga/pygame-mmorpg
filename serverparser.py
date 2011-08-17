#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import socket, time, random
import thread, string, cPickle
import re

#definir tempo minimo entre um movimento e outro. Esse tempo limita os "hackers" para não sacanearem e colocarem delay pequeno.
DELAY = 1.0 / 7.0

# tempo para movimento dos monstros, em segundos
MONSTER_DELAY = 1

EMPTY = 255

MSG_SIZE = 1024*1024

#mapeando eventos da pygame personalizados
GOTO = 24
MESSAGE = 25
SETOBJECT = 26
SYSTEM = 27
GETINFO = 28
TWITTER = 29

INFO = {
0: 'uma arvore larga',
1: 'uma arvore comprida',
2: 'tinha uma pedra no meio do caminho...',
3: 'Um edificio',
4: 'Um edificio',
5: 'Um edificio',
6: 'Um edificio',
7: 'Um edificio',
8: 'Um edificio',
9: 'Um edificio',
10: 'Um edificio',
13: 'Um edificio',
11: 'um dragao de estimacao',
12: 'O Tesouro!!!',
13: '',
14: '',
15: '',
16: '',
17: '',
18: '',
19: '',
20: 'Um terrivel 10 olhos!',
21: 'O minhocao assassino',
22: 'O lobo mau',
23: 'uma lagosta voadora malvada',
254: '',
255: '',
}
clients = []
objmap = cPickle.load(file('data/objmap.txt', 'r'))
map_y = len(objmap)
map_x = len(objmap[0])

#criando matriz do mapa temporario de objetos (criaturas e outros no server)
tempmap = []
for l in range(map_y):
    tempmap += [ [None] * map_x]


def position_available(x, y):
    """
    retorna se a posicao esta disponivel para movimentacao
    """
    return objmap[y][x] == EMPTY# and tempmap[y][x] == None


def monster_spawner(n):
    """
    criador de monstros aleatorio

    n - numero de monstros a colocar no mapa
    """
    l = 0
    limit = 0
    while l < n and limit < n*n+500:
        limit += 1
        x, y = random.randint(20,490), random.randint(5,495)
        if position_available(x,y):
            addobj(random.randint(20,23), [x,y])
            l += 1

def newpos():
    birth = [0,0]
    while not ( position_available(*birth) and tempmap[birth[1]][birth[0]] == None):
        birth[0] += 1
        if birth[0] >= map_x:
            birth[0] = 0
            birth[1] += 1
        if birth[1] > map_y:
            birth[1] = 0
    return birth

class Client:
    def __init__(self, connection, info, actor=14, pos=None):
        self.actor = actor
        self.name = "no name"
        self.type = "client"
        self.connection, self.info = connection, info
        self.time = time.time()
        if not pos:
            pos = [0,0]
        self.pos = pos
        self.respawn()
        #self.sendgoto(newpos())
        self.msgbuffer = []

    def __str__(self):
        return str("%s (%s)"%( self.name,self.info))

    def recv(self):
        return self.connection.recv(MSG_SIZE)
    
    def sendmsg(self, msg):
        self.msgbuffer += ["Event(25, {'msg': '%s'}),"%msg]
    
    def send(self, msg):
        try:
            self.connection.send(msg)
        except:
            print ">> Nao foi possivel enviar '%s' para '%s'"%(msg, self.name)
            #self.close()
    
    def sendsetobject(self, creature, pos):
        #self.send("Event(26, {'obj': %d, 'x': %d, 'y': %d}),"%(creature, pos[0], pos[1]))
        #setobj(pos,creature, self)
        return actormove(self.pos, pos, self)

    def senddelobject(self, pos):
        self.sendsetobject(255,pos)
    
    def sendgoto(self, pos):
        #se a posicao ja estiver sendo ocupada, mantem a mesma
        if not position_available(pos[0], pos[1]):
            self.send("Event(24, {'x': %d, 'y': %d}),"%(self.pos[0], self.pos[1]))
        else:
            self.send("Event(24, {'x': %d, 'y': %d}),"%(pos[0], pos[1]))
            #self.senddelobject(self.pos)
            if self.sendsetobject(self.actor, pos):
                self.pos = pos

    def close(self):
        self.send("Event(QUIT),")
        self.delete()

    def delete(self):
        self.connection.close()
        tempmap[self.pos[1]][self.pos[0]] = None
        clients.remove(self)

    def kill(self):
        self.sendmsg("Voce morreu!!!")
        self.respawn()
    
    def checktime(self):
        #print time.time() - self.time
        if time.time() - self.time > DELAY:
            self.time = time.time()
            return True
        #print time.time(), time.time() - self.time
        #return False
        return True
    
    def getpos(self):
        return self.pos
    
    def parse(self, msg):
        parse(self, msg)

    def respawn(self):
        pos = newpos()
        self.sendgoto(pos)
        #actormove(self.pos, pos, self)

class NPC:
    def __init__(self, code, pos):
        self.actor = code
        self.pos = pos
        self.name = INFO[code]
        self.move(pos)
        self.type = "npc"

    def send(self, msg):
        pass
    
    def move(self, pos):
        if pos[0] <= -map_x/2:
            pos[0] += map_x
        if pos[1] <= -map_y/2:
            pos[1] += map_y
        if pos[0] >= map_x/2:
            pos[0] -= map_x
        if pos[1] >= map_y/2:
            pos[1] -= map_y
        actormove(self.pos, pos, self)
        self.pos = pos


monsters = []

def addobj(code, pos):
    global monsters
    obj = NPC(code, pos)
    if code >= 20:
        #print "adding %s (%s) on %s"%(obj, code, pos)
        monsters += [obj]
    tempmap[pos[1]][pos[0]] = obj

def delobj(pos):
    global monsters
    obj = tempmap[pos[1]][pos[0]]
    if obj:
        if obj.actor >= 20:
            monsters.remove(obj)
        tempmap[pos[1]][pos[0]] = None


def monstersmove():
    while True:
        for creature in monsters:
            pos = creature.pos
            tempmap[pos[1]][pos[0]] = None
            newpos = None
            for j in range(pos[1]-1, pos[1]+2):
                for i in range(pos[1]-1, pos[1]+2):
                    if tempmap[j][i] and tempmap[j][i].type == "client":
                        newpos = [i,j]
            if newpos == None:
                i, j = random.randint(pos[0]-1,pos[0]+1), random.randint(pos[1]-1,pos[1]+1)
                while objmap[j][i] != 255:
                    i, j = random.randint(pos[0]-1,pos[0]+1), random.randint(pos[1]-1,pos[1]+1)
                newpos = [i,j]
            creature.move(newpos)
            #print "Monster %s moved to %s"%(creature.actor, newpos)
        time.sleep(MONSTER_DELAY)
            

# movimento de alguma criatura, NPC ou char
def actormove(oldpos, newpos, actor=None):
    global tempmap
    if not actor:
        actor = getactor(oldpos)

    # se nao se movimentou...
    if tuple(oldpos) == tuple(newpos):
        #nothing need to be done
        return False

    #verificando conflitos
    obj = tempmap[newpos[1]][newpos[0]]
    if obj:
        if actor.type == "npc" and obj.type == "client" and obj.name != "FaGa":
            obj.kill()
            obj.sendmsg("%s te matou!!!"%actor.name)
        elif actor.type == "client" and obj.type == "npc" and obj.name != "FaGa":
            actor.kill()
            actor.sendmsg("%s te matou!!!"%obj.name)
            return False
        elif actor.type == "client" and obj.type == "client":
            obj.kill()
            obj.sendmsg("%s te matou!!!"%actor.name)
            actor.sendmsg("vc matou o/a %s!!"%obj.name)
            if obj.name == "FaGa":
                print ">>>>>> %s matou o Faga!!!!!!!!!!!!!"%actor.name
                while True:
                    time.sleep(1)
                    for c in clients:
                        c.kill()
    
    tempmap[oldpos[1]][oldpos[0]] = None
    tempmap[newpos[1]][newpos[0]] = actor

    rms, adds = [], []
    # como realizamos um movimento, vamos atualizar os clientes das vizinhancas.
    # note que isso eh experimental, pois para o cliente a cada movimento eh atualizada a vizinhanca mesmo que inalterada.
    for j in range(-7, 8):
        for i in range(-9, 10):
            ### removendo o objeto da posicao anterior para os clientes conectados
            obj =  tempmap[j + oldpos[1]][i + oldpos[0]]
            if obj and 12 <= obj.actor:
                if obj.type == "client":
                    rms += [(obj, "Event(26, {'obj': %d, 'x': %d, 'y': %d}),"%(255, oldpos[0], oldpos[1]))]
                if obj != actor:
                    rms += [(actor, "Event(26, {'obj': %d, 'x': %d, 'y': %d}),"%(255, i + oldpos[0], j + oldpos[1]))]

            #inserindo o objeto na nova posicao
            obj =  tempmap[j + newpos[1]][i + newpos[0]]
            if obj and 12 <= obj.actor:
                if obj.type == "client":
                    adds += [(obj, "Event(26, {'obj': %d, 'x': %d, 'y': %d}),"%(actor.actor, newpos[0], newpos[1]))]
                if obj != actor:
                    adds += [(actor, "Event(26, {'obj': %d, 'x': %d, 'y': %d}),"%(obj.actor, i + newpos[0], j + newpos[1]))]

    #print oldpos, newpos, rms, adds
    for r in rms:
        r[0].send(r[1])
    for a in adds:
        a[0].send(a[1])
    return True

def senderror(client, msg):
    client.send("Event(27, {'msg': '%s'}),"%msg)

#compilar o pattern para encontrar o dicionario e o tipo do evento
patt = re.compile("(?<=Event)[^\>]+")


def parse(client, msg):
    """ Avalia um conjunto de eventos em formato string str(Event)"""
    evts = patt.findall(msg)
    for e in evts:
        parseevt(client, e)


def getactor(pos):
    for cli in clients:
        #procuramos algum client nessa posicao
        acpos = cli.getpos()
        if tuple(acpos) == tuple(pos):
            return cli
    return None

def parseevt(client, msg):
    """ Avalia um evento em formato string """
    global clients
    
    #GOTO:
    if "(24-" in msg[:5]:
        msg = msg[13:-1]
        try:
            pos = eval(msg)
            pos = [pos['x'], pos['y']]
            deltax, deltay = abs(pos[0] - client.pos[0]) , abs(pos[1] - client.pos[1])
            if client.checktime():
                #print client.pos, pos, deltax, deltay
                if deltax > 1 or deltay > 1:
                    senderror(client,"posicao invalida (%d, %d) - normalizando para (%d, %d), movendo (%d, %d),"% (deltax, deltay, pos[0], pos[1], pos[0] / max(abs(pos[0]), 1), pos[1] / max(abs(pos[1]), 1)))
                    if deltax != 0:
                        pos[0] = client.pos[0] + deltax / (pos[0] - client.pos[0])
                    if deltay != 0:
                        pos[1] = client.pos[1] + deltay / (pos[1] - client.pos[1])
                if pos[0] <= -map_x/2:
                    pos[0] += map_x
                if pos[1] <= -map_y/2:
                    pos[1] += map_y
                if pos[0] >= map_x/2:
                    pos[0] -= map_x
                if pos[1] >= map_y/2:
                    pos[1] -= map_y
                client.sendgoto(pos)
            else:
                client.sendgoto(client.pos)
                senderror(client,'Nao envie mais movimentos em intervalos menor de 0.12 segundos!!')
        except:
            senderror(client,'Erro, sua posicao nao e um numero valido.')
    
    #GETINFO
    elif "(28-" in msg[:5]:
        msg = msg[13:-1]
        try:
            click = eval(msg)
            pos = click['pos']
            m = INFO[objmap[pos[1]][pos[0]]]
            #checamos se e um ator (player)
            if tempmap[pos[1]][pos[0]]:
                ac = getactor(pos)
                if ac:
                    m = ac.name
            #se houve alguma mensagem
            if m:
                client.sendmsg("info: "+m)
        except:
            print ">> cliente %s perguntou de um objeto estranho"%client

    #System (apresentacao, id e nome)
    elif "(27-" in msg[:5]:
        #print msg
        msg = msg[13:-1]
        try:
            l = eval(msg)
            if len(l) == 2:
                client.name = l['name']
                if client.name == "FaGa" and client.info[0] != "127.0.0.1":
                    client.close()
                if 14 <= l['id'] <= 19:
                    client.actor = l['id']
                else:
                    client.actor = 14
                    senderror(client, "Sua ID de usuario e invalida, escolha entre 14 e 19.")
        except:
            print ">> Veio uma mensagem estranha de um cliente: '%s'"%msg
            senderror(client, "Erro, aparentemente sua mensagem SYSTEM esta incorreta")

    #Twitter (lista de amigos de entrada, lista de onlines retornada)
    elif "(29-" in msg[:5]:
        #print msg
        msg = msg[13:-1]
        try:
            l = eval(msg)
            if len(l) == 1:
                friends = l['friends']
                online = []
                for c in clients:
                    if c.name in friends:
                        online += [c.name]
                client.send("Event(29, {'msg': %s}),"%online)
        except:
            print ">> Veio uma mensagem estranha de um cliente: '%s'"%msg
            senderror(client, "Erro, aparentemente sua mensagem TWITTER esta incorreta")
    else:
        print msg
