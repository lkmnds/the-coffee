import libcoffee
import socket

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

VERSION = '0.0.1'

HOST = 'localhost'

def main():
    print("coffee client v%s" % VERSION)

    s = socket.socket()
    s.connect((HOST, libcoffee.PORT))

    cs = libcoffee.cli_handshake(s)
    print(cs)
    ok, err = cs.exit_gracefully()
    if ok:
        print("Exited gracefully")
    else:
        print("Error:")

if __name__ == '__main__':
    main()
