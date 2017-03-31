import libcoffee2 as libcoffee
import socket

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

VERSION = '0.0.1'
HOST = 'localhost'

cs = libcoffee.ClientState(id='someone')

def main():
    print("coffee client v%s" % VERSION)

    cs.connect(HOST)
    cs.close()

if __name__ == '__main__':
    main()
