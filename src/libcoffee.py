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
    return recvall(sock, length)

class CoffeeState:
    def __init__(self, sock, init_string):
        self.socket = sock
        self.acc_methods = []
        self.parse_hd(init_string)

    def parse_hd(self, s):
        self.acc_methods = s.split(' ')

class BrewState(object):
    def __init__(self, sock):
        self.sock = sock
        self.parse_hd()

    def parse_hd(self):
        recv_msg(self.sock)

def cli_handshake(sock):
    send_msg(sock, "HAI MACHINE;FEATURES\n")
    cs = CoffeeState(sock, recv_msg(sock))
    send_msg(sock, "ALLRIGHT\n")
    return cs

def ser_handshake(sock):
    bs = BrewState(sock)
    return bs

def auth(cs, password):
    send_msg(cs.sock, "AUTH %s\n" % password)

def auth2(cs, password):
    return
