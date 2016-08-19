import libcoffee
import socket

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
    if cs.exit_gracefully():
        print("Exited gracefully")

if __name__ == '__main__':
    main()
