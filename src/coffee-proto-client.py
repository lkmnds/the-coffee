import libcoffee2 as libcoffee
import socket
import time

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

VERSION = '0.0.1'
HOST = 'localhost'

cs = libcoffee.ClientState(name='ExampleClient')

def main():
    print("coffee client v%s" % VERSION)

    cs.connect(HOST)

    user = input('user: ')
    password = input('pass: ')
    cs.authenticate(user, password)

    t1 = time.monotonic()
    cs.ping()
    t2 = time.monotonic()
    delta = (t2 - t1) * 1000
    print("Ping: %.2fms" % delta)

    cs.close()

if __name__ == '__main__':
    main()
