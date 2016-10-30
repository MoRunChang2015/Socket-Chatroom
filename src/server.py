import socket
import sys
import thread
from protocol import *

RECV_BUFFER = 4096
HOST = 'localhost'
PORT = 8000
LINE = "----------------------------------------"

class ChatRoomServer(socket.socket):
    def __init__(self, host, port):
        super(ChatRoomServer, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket binding port: ' + str(port) + '.')
        try:
            self.sock.bind((host, port))
        except socket.error:
            print('Bind failed.')
            sys.exit(0)
        self.sock.listen(5)
        print('Socket listening on port: ' + str(port) + '...')
        print LINE
        self.users = {}

    def handleSocketAccept(self):
        while True:
            conn, addr = self.sock.accept()
            thread.start_new_thread(self.handleUserConnect, (conn, addr))

    def handleUserConnect(self, conn, addr):
        package = conn.recv(RECV_BUFFER)
        print package
        print LINE
        req = handleReuest(package)
        if (req.getType() != "HELLO"):
            return
        username = req.getName()
        print("New connection from %s(%s:%s)." % (username, addr[0], addr[1]))
        self.users[username] = conn
        msg = username + " entered the chat room."
        package = generateRequest('SYST', 'Server', msg)
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
                package = generateRequest('SYST', 'Server', msg)
                self.broadcast(package)
                return

    def broadcast(self, content):
        for username in self.users:
            self.users[username].sendall(content)


if __name__ == "__main__":
    server = ChatRoomServer(HOST, PORT)
    try:
        server.handleSocketAccept()
    except KeyboardInterrupt:
        print("Server shutdown.")
    finally:
        server.close()
