import socket
import sys
import thread
from protocol import *

LINE = "----------------------------------------"
class ChatServer(socket.socket):
    def __init__(self, host, port):
        super(ChatServer, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created.')
        try:
            self.sock.bind((host, port))
        except socket.error:
            print('Bind failed.')
            sys.exit(0)
        self.sock.listen(5)
        print('Socket listening...')
        self.users = {}

    def handle_accept(self):
        while True:
            conn, addr = self.sock.accept()
            thread.start_new_thread(self.handle_single_connect, (conn, addr))

    def handle_single_connect(self, conn, addr):
        username = conn.recv(RECV_BUFFER)
        print("New connection from %s(%s:%s)." % (username, addr[0], addr[1]))
        self.users[username] = conn
        msg = username + " entered the chat room."
        package = generateRequest('SYST', 'Admin', msg)
        self.broadcast(package)

        while True:
            package = conn.recv(RECV_BUFFER)
            if not package:
                continue
            print(package)
            print LINE
            req = handleReuest(package)
            if req.getType() == 'SEND':
                self.broadcast(package)
            elif req.getType() == 'EXIT':
                self.users.pop(req.getName())
                print("Connection with %s(%s:%s) ended." %
                      (username, addr[0], addr[1]))
                msg = username + " exited the chat room."
                package = generateRequest('SYST', 'Admin', msg)
                self.broadcast(package)

    def broadcast(self, content):
        for username in self.users:
            self.users[username].sendall(content)


if __name__ == "__main__":

    RECV_BUFFER = 4096
    HOST = 'localhost'
    PORT = 8000
    server = ChatServer(HOST, PORT)
    try:
        server.handle_accept()
    except KeyboardInterrupt:
        print("Server shutdown.")
    finally:
        server.close()
