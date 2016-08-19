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
    'AUTH_NOAUTH': 'Authentication is disabled for this server',
}

class CoffeeError:
    def __init__(self, msg):
        self.s = ''
        self.msg = msg
        self.translated = error_trans[msg]

    def __repr__(self):
        return 'CoffeeError(%s)' % self.translated

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
        res = self.receive()
        print("recv : %s" % res)
        if res == 'HAI':
            return True, None
        else:
            return False, CoffeeError(res)

    def send(self, m):
        send_msg(self.sock, m)

    def receive(self):
        return recv_msg(self.sock)

    def recv_allright(self):
        msg = self.receive()
        if msg == "ALLRIGHT":
            return True, ''
        else:
            return False, 'recv: %s' % msg

    def exit_gracefully(self):
        self.send("EXIT")
        return self.recv_allright()

    def target(self, target_name):
        if target_name in self.acc_methods:
            self.send("TARGET %s" % target_name)
            return self.recv_allright()
        else:
            return False, 'Method doesn\'t exist'

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
        return 'Order(%d, %s)' % (self.order_id, self.order_name)

class Orders:
    def __init__(self):
        self.orders = []
        self.last_id = 0

    def new_order(self, order_str):
        o = Order(order_str, self.last_id + 1)
        logging.debug("New Order: %r" % o)
        self.orders.append(o)
        self.last_id += 1

class MachineState:
    def __init__(self, name, password):
        self.orders = Orders()
        self.name = name
        self.password = password

    def new_order(self, order_str):
        self.orders.new_order(order_str)

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

    def send(self, m):
        send_msg(self.sock, m)

    def receive(self):
        return recv_msg(self.sock)

    def parse_msg(self):
        s = recv_msg(self.sock)
        for cmd in s.split(';'):
            cmds = cmd.split(' ')
            if cmd == "HAI MACHINE":
                # init data, session, etc
                self.sessions[hash(self.sock)] = {
                    'sock': self.sock,
                    'auth': False,
                }
            elif cmd == "FEATURES":
                self.send(' '.join(self.features))
                # self.allright()
            elif cmd == "NAME":
                send_msg(sock, self.name)
            elif cmds[0] == "AUTH":
                if "AUTH" in self.features:
                    # make Authentication
                    pwd = cmds[1]
                    logging.debug("AUTH: %s" % pwd)
                    if pwd == self.ms.password:
                        logging.debug("Authentication: Correct")
                        self.sessions[hash(self.sock)]['auth'] = True
                        self.send("HAI")
                    else:
                        logging.debug("Wrong Password")
                        self.sessions[hash(self.sock)]['auth'] = False
                        self.send("AUTH_NOPE")
                else:
                    self.send("AUTH_NOAUTH")
            elif cmds[0] == "TARGET":
                if "AUTH" in self.features:
                    # Reject if not authenticated
                    hs = hash(self.sock)
                    if (hs not in self.sessions) or \
                        (not self.sessions[hs]['auth']):
                        self.rejected()
                    elif self.sessions[hs]['auth']:
                        order = ' '.join(cmds[1:])
                        self.ms.new_order(order)
                        self.allright()
                    else:
                        self.send("REJC:AUTH:else")
                else:
                    order = ' '.join(cmds[1:])
                    self.ms.new_order(order)
                    self.allright()
            elif cmd == "EXIT":
                del self.sessions[hash(self.sock)]
                logging.debug("%d exiting" % hash(self.sock))
                self.allright()
                return False
        return True

    def allright(self):
        self.send("ALLRIGHT")

    def rejected(self):
        self.send("REJECTED")

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
