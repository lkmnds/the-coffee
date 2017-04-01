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

# authentication
OP_AUTHENTICATE = 15
OP_AUTH_NOT_NEEDED = 16
OP_AUTH_SUCCESS = 17
OP_AUTH_FAILURE = 18

OP_WRONG_DATA = 20
OP_CLOSE = 30

def send_op(sock, op, data):
    payload = {'op': op}
    payload = {**payload, **data}

    if '_timestamp' not in payload:
        payload['_timestamp'] = time.time()

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
    def __init__(self, conn_id, sock, ms):
        self.id = conn_id
        self.sock = sock
        self.ms = ms
        self.operations = {
            OP_PING: self.do_ping,
            OP_AUTHENTICATE: self.do_auth,
        }

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

    def do_ping(self, data):
        send_op(self.sock, OP_PING_ACK, {})
        return True

    def do_auth(self, data):
        if not self.ms.auth_required:
            send_op(self.sock, OP_AUTH_NOT_NEEDED, {})
            return True

        user = data['user']
        password = data['password']

        if not constant_compare(user, self.default_user[0]):
            send_op(self.sock, OP_AUTH_FAILURE, {})
            return True

        if not constant_compare(password, self.default_user[1]):
            send_op(self.sock, OP_AUTH_FAILURE, {})
            return True

        self.authenticated = True
        send_op(self.sock, OP_AUTH_SUCCESS, {})
        return True

    def recv(self):
        data = recv_op(self.sock)

        if data['op'] == OP_CLOSE:
            logger.info("[recv:%s] Closing", self.id)
            send_op(self.sock, OP_CLOSE, {})
            self.sock.close()
            return False
        else:
            op = data['op']
            if op in self.operations:
                func = self.operations[op]
                return self.func(data)
            else:
                logger.info('[recv:%s] Invalid operator code', self.id)
                send_op(self.sock, OP_WRONG_DATA, {
                    'unhandled': op
                })
                self.sock.close()
                return False

        time.sleep(1)
        return True

    def close(self):
        logger.info("[client:%s] closing", self.id)
        send_op(self.sock, OP_CLOSE, {})
        self.sock.close()

class MachineState:
    def __init__(self, **kwargs):
        name = kwargs.get('name')
        default_user = kwargs.get('default_user')

        self.auth_required = True
        if default_user is None:
            self.auth_required = False

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

        cc = ClientConnection(conn_id, sock, self)
        self.clients[conn_id] = cc

        # handshake + main loop
        cc.handshake()

        while cc.recv():
            pass

        # if the loop ended, remove the ClientConnection
        del self.clients[conn_id]

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
        })

        return time.time() - data['_timestamp']

    def ping(self):
        logger.debug('[client:%s] send OP_PING', self.id)

        send_op(self.sock, OP_PING, {})
        recv_op(self.sock, OP_PING_ACK)

        return True

    def authenticate(self, user, password):
        send_op(self.sock, OP_AUTHENTICATE, {
            'user': user,
            'password': password,
        })

        data = recv_op(self.sock)
        op = data['op']

        if op == OP_AUTH_NOT_NEEDED:
            logger.debug('[auth:%s] authentication not needed', self.id)
            return True
        elif op == OP_AUTH_FAILURE:
            logger.debug('[auth:%s] Failure to authenticate', self.id)
            return False
        elif op == OP_AUTH_SUCCESS:
            return True

        logger.info('[auth:%s] Operation %d not found', self.id, op)
        return False

    def close(self):
        logger.info("[client:%s] closing", self.id)

        send_op(self.sock, OP_CLOSE, {})
        recv_op(self.sock, OP_CLOSE)

        self.sock.close()
