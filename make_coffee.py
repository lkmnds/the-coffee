import socket
import sys
import time

BUFSIZE = 1024

args = sys.argv

'''
    Disclaimer here:
         * I don't own any coffee TCP-enabled machine.
         * This code is based on the fucking-coffee.py script on the original repo
         * The coffee protocol still needs documentation
'''

def main():
    COFFEE_IP = '0.0.0.0'
    COFFEE_PORT = 80
    if len(args) == 3:
        COFFEE_IP = args[1]
        COFFEE_PORT = int(args[2])

    s = socket.socket()
    s.connect((COFFEE_IP, COFFEE_PORT))

    passwd = input("password: ")
    s.send("HI_COFFEE %s/n" % (passwd,))
    
    header = s.recv(BUFSIZE)
    if header == 'COFFEE_OK':
        s.send("CMD brew/n")
        time.sleep(24)
        s.send("CMD pour/n")
    else:
        print("no coffee")

if __name__ == '__main__':
    main()
