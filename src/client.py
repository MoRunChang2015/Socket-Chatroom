import socket
import sys
import thread
import Tkinter as tk
from time import sleep
from protocol import *
LINE = "----------------------------------------"

class ChatRoomClient():
    def __init__(self, username):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = username

    def connect(self, host, port, timeout=10):
        self.sock.connect((host, port))
        self.sock.settimeout(timeout)

    def setUserName(self, username):
        self.username = username

    def close(self):
        self.sock.close()

    def receive(self):
        return self.sock.recv(RECV_BUFFER)

    def send(self, message):
        self.sock.sendall(message)

class ChatFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.publicText = tk.Text(self, width=60, height=20)
        self.inputText = tk.Text(self, width=60, height=5)
        self.sendButoon = tk.Button(self, text='send', command=self._send)
        self.clearButton = tk.Button(self, text='clear', command=self._clear)
        self.exitButton = tk.Button(self, text='exit', command=self._exit)
        self._createWidgets()
        self.grid()
        thread.start_new_thread(self._receiveMessage, ())

    def _createWidgets(self):
        self.publicText.grid(column=0, row=0, columnspan=3)
        self.inputText.grid(column=0, row=1, columnspan=3, rowspan=2)
        self.sendButoon.grid(column=2, row=3)
        self.clearButton.grid(column=1, row=3)
        self.exitButton.grid(column=0, row=3)

    def _send(self):
        msg = self.inputText.get(1.0, tk.END).strip()
        if msg is None or len(msg) == 0:
            return
        package = generateRequest('SEND', client.username, msg)
        client.send(package)
        self.inputText.delete(1.0, tk.END)

    def _clear(self):
        self.publicText.delete(1.0, tk.END)

    def _receiveMessage(self):
        while True:
            sleep(SLEEP_TIME)
            try:
                package = client.receive()
                print(package)
                print LINE
                req = handleReuest(package)
                self.tk = tk.Frame
                # Handle with the package received.
                if req.getType() == 'SEND':
                    msg = req.getData()
                    time = readTime(req.getTime())
                    output = req.getName() + "  " + time + "\n" + msg + "\n"
                    self.publicText.insert(tk.INSERT, output)
                elif req.getType() == 'SYST':
                    msg = req.getData()
                    time = readTime(req.getTime())
                    output = msg + " (" + time + ") " + "\n"
                    self.publicText.insert(tk.INSERT, output)

            except socket.error:
                continue

    def _exit(self):
        try:
            package = generateRequest('EXIT', username)
            client.send(package)
            client.close()
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage : python client.py hostname port')
        sys.exit()
    host = sys.argv[1]
    port = int(sys.argv[2])
    RECV_BUFFER = 4096
    SLEEP_TIME = 0.5

    username = raw_input("Please enter your name: ").strip()
    client = ChatRoomClient(username)
    try:
        client.connect(host, port)
        print("Connection succeeded.")
    except Exception as e:
        print e
        print("Connection failed.")
        sys.exit(0)
    msg = "Hello, I'm " + username + "."
    package = generateRequest('HELLO', username, msg)
    client.send(package)
    while True:
        package = client.receive()
        req = handleReuest(package)
        print req.getType()
        if req.getType() != "ERROR":
            break
        print "username illegal, please input a new one"
        username = raw_input("Please enter your name: ").strip()
        print LINE
        msg = "Hello, I'm " + username + "."
        package = generateRequest('HELLO', username, msg)
        client.send(package)

    client.setUserName(username)
    app = ChatFrame()
    app.master.title(username + '@chatroom')
    app.mainloop()
