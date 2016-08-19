import time
import socket
import datetime
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

VERSION = '0.0.2'

HOST = 'localhost'
PORT = 8001

threads = []
global_state = MachineState()

def new_client(cli, sock):
    global global_state
    logging.debug("New thread")

    bs = ser_handshake(sock, global_state)

    logging.debug("Exiting thread")

def main():
    global threads

    print("coffee client v%s" % VERSION)
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(CLISIZE)
    try:
        while True:
            con, cli = s.accept()
            t = threading.Thread(name=cli[0] + '-' + str(cli[1]), target=new_client, args=(cli, con))
            threads.append(t)
            t.start()
    except KeyboardInterrupt:
        print("exit")
        s.close()
        return

if __name__ == '__main__':
    main()
