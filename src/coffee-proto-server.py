import time
import socket
import datetime

VERSION = '0.0.1'

def main():
    print("coffee client v%s" % VERSION)
    s = socket.socket()
    #etc...
    while True:
        sock, con = s.accept()

if __name__ == '__main__':
    main()
