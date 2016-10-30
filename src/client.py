import socket
import sys
import thread
import Tkinter as tk
from time import sleep
from protocol import *
LINE = "----------------------------------------"
class ChatFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.publicText = tk.Text(self, width=60, height=20)
        self.inputText = tk.Text(self, width=40, height=5)
        self.sendButoon = tk.Button(self, text='send', command=self.__send)
        self.clearButton = tk.Button(self, text='clear', command=self.__clear)
        self.exitButton = tk.Button(self, text='exit', command=self.__exit)
        self.__create_widgets()
        self.grid()
        thread.start_new_thread(self.__receive_message, ())
        client.sendall(client.username)

    def __create_widgets(self):
        self.publicText.grid(column=0, row=0, columnspan=3)
        self.inputText.grid(column=0, row=1, columnspan=3, rowspan=2)
        self.sendButoon.grid(column=0, row=3)
        self.clearButton.grid(column=1, row=3)
        self.exitButton.grid(column=2, row=3)

    def __send(self):
        msg = self.inputText.get(1.0, tk.END).strip()
        if msg is None or len(msg) == 0:
            return
        package = generateRequest('SEND', username, msg)
        client.sendall(package)
        self.inputText.delete(0.0, tk.END)

    def __clear(self):
        self.publicText.delete(0.0, tk.END)

    def __receive_message(self):
        while True:
            sleep(SLEEP_TIME)
            try:
                package = client.receive()
                print(package)
                print LINE
                req = handleReuest(package)
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

    def __exit(self):
        package = generateRequest('EXIT', username)
        client.sendall(package)
        client.close()
        sys.exit(0)


class ChatClient(socket.socket):
    def __init__(self, username):
        socket.socket.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = username

    def connect(self, host, port, timeout=10):
        self.sock.connect((host, port))
        self.sock.settimeout(timeout)

    def close(self):
        self.sock.close()

    def receive(self):
        return self.sock.recv(RECV_BUFFER)

    def sendall(self, message):
        self.sock.sendall(message)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage : python client.py hostname port')
        sys.exit()
    host = sys.argv[1]
    port = int(sys.argv[2])
    username = raw_input("Please enter your name: ").strip()
    RECV_BUFFER = 4096
    SLEEP_TIME = 0.5
    client = ChatClient(username)
    try:
        client.connect(host, port)
        print("Connection succeeded.")
    except Exception as e:
        print("Connection failed.")
        sys.exit(0)
    app = ChatFrame()
    app.master.title(username + '@chatroom')
    app.mainloop()
