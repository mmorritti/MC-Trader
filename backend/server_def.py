import socket
import threading


class Server:
    def __init__(self, address, port, name, debug=False):
        self.address   = str(address)
        self.port      = int(port)
        self.debug     = bool(debug)
        self.name      = str(name)
        self.clients   = []
        self.addresses = []
        self.names     = []

        self.server    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.address, self.port))

        accept_thread = threading.Thread(target=self.accept)
        accept_thread.start()


    def accept(self):
        self.server.listen()

        while True:
            try:
                client, address = self.server.accept()
                self.out(f"{str(address)} is now connected to the server")

                self.clients.append(client)
                self.addresses.append(address)

                connect_thread = threading.Thread(target=self.on_connect, args=(client, address))
                connect_thread.start()
            except Exception as e:
                self.out("Client failed to connect to the server")


    def on_connect(self, client, address):
        handle_thread = threading.Thread(target=self.handle, args=(client, address, "Generic Client"))
        handle_thread.start()


    def handle(self, client, address, name):
        self.names.append(name)

        while True:
            try:
                client.sendall("[Internal] CLN_INPUT".encode("utf-8"))
                message = client.recv(1024).decode("utf-8")
            except Exception as e:
                if client in self.clients:
                    self.clients.remove(client)
                    self.addresses.remove(address)
                    self.names.remove(name)

                self.out(f"\n\nServer Raised Exception:\n\t{e}")
                client.close()
                self.out(f"{name} lost connection")
                break


    def ask_client(self, question, client):
        client.sendall(question.encode("utf-8"))
        return client.recv(1024).decode("utf-8")


    def out(self, text):
        if self.debug:
            if "\n" not in text:
                print(f"[{self.name}] {text}")
            else:
                print(text)
