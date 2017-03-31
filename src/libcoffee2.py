#!/usr/bin/env python3

import time
import socket
import json
import uuid

import struct
import logging
import hashlib
from collections import namedtuple

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

def send_json(sock, _dict):
    data = json.dumps(_dict)
    return send_msg(sock, data)

OP_IDENTIFY = 2
OP_INVALID = 9

# HELLO payloads, used on handshake
OP_HELLO = 10
OP_HELLO_ACK = 11

OP_PING = 12
OP_PING_ACK = 13

OP_WRONG_DATA = 20
OP_CLOSE = 30

def send_op(sock, op, data):
    payload = {'op': op}
    payload = {**payload, **data}
    print('send', payload)
    return send_json(sock, payload)

def recv_json(sock):
    return json.loads(recv_msg(sock))

def recv_op(sock, op=None):
    data = recv_json(sock)
    print('recv', data)
    if op is not None and data['op'] != op:
        send_op(sock, OP_WRONG_DATA, {
            'expected': op,
            'received': data['op']
        })
        return None
    return data

# Modification of http://security.stackexchange.com/a/83671
def constant_compare(val1, val2):
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0

logger = logging.getLogger('coffee')

class ClientConnection:
    def __init__(self, conn_id, sock):
        self.id = conn_id
        self.sock = sock

    def handshake(self):
        hello_timestamp = time.time()

        # send HELLO
        send_op(self.sock, OP_HELLO, {
            'id': self.id,
            '_timestamp': hello_timestamp
        })

        # wait for ACK
        data = recv_op(self.sock, OP_HELLO_ACK)
        delta = (data['_timestamp'] - hello_timestamp)

        logger.info("[handshake:%s] HELLO_ACK, time taken : %.2fms", \
            self.id, delta * 1000)

        return delta

    def recv(self):
        time.sleep(1)
        return True

class MachineState:
    def __init__(self, **kwargs):
        name = kwargs.get('name')
        default_user = kwargs.get('default_user', (None, None))
        self.clients = {}

    def new_id(self):
        tries = 0
        new_id = str(uuid.uuid4().fields[-1])[:5]
        while new_id in self.clients:
            if tries > 5: return None
            new_id = str(uuid.uuid4().fields[-1])[:5]
            tries += 1

        return new_id

    def new_client(self, sock):
        conn_id = self.new_id()

        cc = ClientConnection(conn_id, sock)
        self.clients[conn_id] = cc

        # handshake + main loop
        cc.handshake()

        while cc.recv():
            pass

class ClientState:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.sock = None
        self.id = None

    def connect(self, ip):
        self.sock = socket.socket()
        self.sock.connect((ip, PORT))

        self.do_handshake()

    def do_handshake(self):
        # first, wait for HELLO
        data = recv_op(self.sock, OP_HELLO)

        self.id = data['id']

        logger.info("[handshake:%s] HELLO payload: %.2f", \
            self.id, data['_timestamp'])

        # send HELLO_ACK
        send_op(self.sock, OP_HELLO_ACK, {
            'id': self.id,
            '_timestamp': time.time(),
        })

        return time.time() - data['_timestamp']
