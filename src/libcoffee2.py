#!/usr/bin/env python3

import time
import socket
import json

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

def send_op(sock, op, data):
    payload = {'op': op}
    payload = {**payload, **data}
    return send_json(sock, payload)

def recv_json(sock):
    return json.loads(recv_msg(sock))

def recv_op(sock, op=None):
    data = recv_json(sock)
    if op is not None and data['op'] != op:
        send_op(sock, OP_WRONG_DATA, {
            'expected': op,
            'received': data['op']
        })

# Modification of http://security.stackexchange.com/a/83671
def constant_compare(val1, val2):
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0

logger = logging.getLogger('coffee')

class Handshaker:
    def __init__(self, _id, sock):
        self.sock = sock
        self.id = _id

    def hs_client(self):
        # first, wait for HELLO
        data = recv_op(self.sock, OP_HELLO)
        if data['op'] == OP_HELLO:
            logger.info("[handshake:%s] HELLO payload: %.2f", \
                self.id, data['_timestamp'])

        # send HELLO_ACK
        send_op(self.sock, OP_HELLO_ACK, {
            'id': self.id,
            '_timestamp': time.time(),
        })

        return {
            'time_taken': time.time() - data['_timestamp']
        }

    def hs_server(self):
        hello_timestamp = time.time()
        # send HELLO
        send_op(self.sock, OP_HELLO, {
            'id': self.id,
            '_timestamp': hello_timestamp
        })

        # wait for ACK
        data = recv_op(self.sock, OP_HELLO_ACK)

        delta = (data['_timestamp'] - hello_timestamp) * 1000
        logger.info("[handshake:%s] HELLO_ACK, time taken : %.2fms", \
            self.id, delta)

        return {
            'time_taken': delta
        }

class MachineState:
    def __init__(self, **kwargs):
        name = kwargs.get('name')
        default_user = kwargs.get('default_user', (None, None))
        self.connections = {}

    def new_client(self, sock):
        conn_id = 'test'
        conn = Connection(sock, conn_id)
        self.connections[conn_id] = conn

        while conn.get_message():
            pass

    def get_conn(self, connection_id):
        return self.connections.get(connection_id)

    def close_conn(self, conn_id):
        conn = self.get_conn(connection_id)
        conn.close_conn()

class ClientState:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'nothing')

    def connect(self, ip):
        s = socket.socket()
        s.connect((ip, PORT))

class Connection(Handshaker):
    def __init__(self, sock, _id):
        Handshaker.__init__(self, _id, sock)
        self.state = {}

    def get_message(self):
        payload = recv_op(self.sock)
        print(payload)

        # custom function
        if hasattr(self, 'do_payload'):
            self.do_payload(payload)

def connect(ip):
    cs = ClientState(ip)
    cs.do_cli_handshake()
    return cs
