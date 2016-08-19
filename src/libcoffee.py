#!/usr/bin/env python3

import struct
import logging

PORT = 8001

# helpers for TCP
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def send_msg(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(b'%s' % bytes(data, 'utf-8'))

def recv_msg(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length).decode('utf-8')

error_trans = {
    'AUTH_NOPE': 'Wrong Password',
}

class CoffeeError:
    def __init__(self, msg):
        self.s = ''
        self.msg = msg

class CoffeeState:
    def __init__(self, sock, init_string):
        self.sock = sock
        self.acc_methods = []
        self.name = 'None'
        self.parse_hd(init_string)

    def parse_hd(self, s):
        sp = s.split(' ')
        self.acc_methods = sp[:-1]
        self.name = sp[-1]
        self.allright()

    def allright(self):
        self.send("ALLRIGHT")

    def auth_one(self, password):
        self.send("AUTH %s" % password)
        res = recv_msg(self.sock)
        if res == 'HAI':
            return True
        else:
            return False, CoffeeError(res)

    def send(self, m):
        send_msg(self.sock, m)

    def receive(self):
        return recv_msg(self.sock)

    def exit_gracefully(self):
        self.send("EXIT")
        if self.receive() == "ALLRIGHT":
            return True
        else:
            return False

    def __repr__(self):
        return 'CoffeeState(%s, %s)' % (self.name, self.acc_methods)

trans = {
    'COFFEE': 'Coffee',
    'HOTCHOC': 'Hot Chocolate',
}

class Order:
    def __init__(self, order_str, order_id):
        self.order_str = order_str
        self.order_name = trans[order_str]
        self.order_id = order_id

    def __repr__(self):
        return 'Order(%d,%s)' % (self.order_id, self.order_name)

class Orders:
    def __init__(self):
        self.orders = []
        self.last_id = 1

    def new_order(order_str):
        self.orders.append(Order(order_str, self.last_id + 1))
        self.last_id += 1

class MachineState:
    def __init__(self, name):
        self.orders = []
        self.name = name

    def new_order(self, order_str):
        self.orders.append(Order(order_str))

class BrewState:
    def __init__(self, sock, features, ms):
        self.sock = sock
        self.ms = ms
        self.name = ms.name
        features.append(ms.name)
        self.features = features
        self.orders = []
        self.sessions = {}
        self.parse_msg()

    def parse_msg(self):
        s = recv_msg(self.sock)
        for cmd in s.split(';'):
            cmds = cmd.split(' ')
            if cmd == "HAI MACHINE":
                # init data, session, etc
                self.sessions[hash(self.sock)] = self.sock
            elif cmd == "FEATURES":
                send_msg(self.sock, ' '.join(self.features))
                self.allright()
            elif cmds[0] == "TARGET":
                order = ' '.join(cmds[1:])
                self.ms.new_order(order)
            elif cmd == "NAME":
                send_msg(sock, self.name)
            elif cmd == "EXIT":
                self.sessions.remove(hash(s))
                print("%d exiting" % hash(s))
                self.allright()

    def allright(self):
        send_msg(self.sock, "ALLRIGHT")

    def __repr__(self):
        return 'BrewState(%s)' % self.features

def cli_handshake(sock):
    send_msg(sock, "HAI MACHINE;FEATURES")
    cs = CoffeeState(sock, recv_msg(sock))
    send_msg(sock, "ALLRIGHT")
    return cs

def ser_handshake(sock, ms=None, features=None):
    if features is None:
        features = ["AUTH", "COFFEE"]
    if ms is None:
        return None
    return BrewState(sock, features, ms)
