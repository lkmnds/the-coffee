import time
import socket
import datetime
import threading
import logging

import libcoffee2 as libcoffee

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

VERSION = '0.0.3'

HOST = 'localhost'
CLISIZE = 3

def do_coffee(cc):
    print("making coffee")
    return True

threads = []
machine = libcoffee.MachineState(name='example_machine', \
    default_user=('user', 'pwd'), drinks={
        'coffee': do_coffee,
    })

def new_client(cli, sock):
    global global_state
    logging.debug("New thread")

    machine.new_client(sock)

    logging.debug("Exiting thread")

def main():
    global threads

    print("coffee server v%s" % VERSION)
    s = socket.socket()
    s.bind((HOST, libcoffee.PORT))
    s.listen(CLISIZE)

    try:
        while True:
            con, cli = s.accept()
            t = threading.Thread(name=cli[0] + '-' + str(cli[1]), target=new_client, args=(cli, con))
            threads.append(t)
            t.start()
    except KeyboardInterrupt:
        print("[server] Exiting")

        for client_id in machine.clients:
            client = machine.clients[client_id]
            client.close()

        s.close()
        return

if __name__ == '__main__':
    main()
