import socket
import sys
import time

import libcoffee

BUFSIZE = 1024

args = sys.argv

def main():
    COFFEE_IP = '0.0.0.0'
    COFFEE_PORT = 80
    if len(args) == 3:
        COFFEE_IP = args[1]
        COFFEE_PORT = int(args[2])

    s = socket.socket()
    s.connect((COFFEE_IP, COFFEE_PORT))

    coffee_state = libcoffee.handshake(s)

    passwd = input("password: ")
    ok, err = libcoffee.auth2(coffee_state, s, passwd)
    if not ok:
        print("error happened: %s" % (err,))

if __name__ == '__main__':
    main()
