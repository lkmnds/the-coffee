import socket
import sys
import time

import libcoffee

BUFSIZE = 1024

args = sys.argv

def main():
    COFFEE_IP = '0.0.0.0'

    if len(args) >= 2:
        COFFEE_IP = args[1]

    s = socket.socket()
    s.connect((COFFEE_IP, libcoffee.PORT))

    coffee_state = libcoffee.cli_handshake(s)

    passwd = input("password: ")
    ok, err = coffee_state.auth2(passwd)
    if not ok:
        print("error happened: %s" % (err,))

if __name__ == '__main__':
    main()
