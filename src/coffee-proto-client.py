import libcoffee2 as libcoffee
import socket
import time
import sys

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

VERSION = '0.0.1'
HOST = 'localhost'

cs = libcoffee.ClientState(name='ExampleClient')

def main(args):
    print("coffee client v%s" % VERSION)

    cs.connect(HOST)

    user = input('user: ')
    password = input('pass: ')
    done = cs.authenticate(user, password)

    if not done:
        print('Error authenticating to the Coffee Machine')
        cs.close()
        return 0

    t1 = time.monotonic()
    cs.ping()
    t2 = time.monotonic()
    delta = (t2 - t1) * 1000
    print("Ping: %.2fms" % delta)

    drinks = cs.get_drinks()
    print('drinks', drinks)

    cs.close()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
