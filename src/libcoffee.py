#!/usr/bin/env python3

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
        self.parse_hd(init_string)

    def parse_hd(self, s):
        self.acc_methods = s.split(' ')
        self.allright()

    def allright(self):
        send_msg(self.sock, "ALLRIGHT")

    def auth_one(self, password):
        send_msg(self.sock, "AUTH %s" % password)
        res = recv_msg(self.sock)
        if res == 'HAI':
            return True
        else:
            return False, CoffeeError(res)

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

class BrewState(object):
    def __init__(self, sock, features):
        self.sock = sock
        self.features = features
        self.orders = []
        self.sessions = {}
        self.parse_hd()

    def parse_msg(self):
        s = recv_msg(self.sock)
        for cmd in s.split(';'):
            cmds = cmd.split(' ')
            if cmd == "HAI MACHINE":
                # init data, session, etc
                self.sessions[hash(self.sock)] = self.sock
                pass
            elif cmd == "FEATURES":
                send_msg(self.sock, ' '.join(self.features))
                self.allright()
            elif cmds[0] == "TARGET":
                order = ' '.join(cmds[1:])
                self.orders.append(Order(order))
            elif cmd == "EXIT":
                self.sessions.remove(hash(s))
                self.allright()

    def allright(self):
        send_msg(self.sock, "ALLRIGHT")

    def parse_hd(self):
        s = recv_msg(self.sock)
        self.parse_msg()

def cli_handshake(sock):
    send_msg(sock, "HAI MACHINE;FEATURES")
    cs = CoffeeState(sock, recv_msg(sock))
    send_msg(sock, "ALLRIGHT")
    return cs

def ser_handshake(sock, features=None):
    if features is None:
        features = ["AUTH", "COFFEE", "HOTCHOC"]
    return BrewState(sock, features)
