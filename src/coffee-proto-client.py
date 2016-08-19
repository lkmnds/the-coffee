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

    ok, err = cs.auth_one(input("password: "))
    if ok:
        print("authenticated")
    else:
        print("error: %s" % err)

    ok, err = cs.target("COFFEE")
    if not ok:
        print("error: %s" % err) # REJECTED if AUTH is enabled
    else:
        print("got target COFFEE")


    ok, err = cs.exit_gracefully()
    if ok:
        print("Exited gracefully")
    else:
        print("Error: %s" % err)

if __name__ == '__main__':
    main()
