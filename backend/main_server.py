from backend.server_def import Server
import threading
import backend.commands as commands
from backend.database import users, stocks, market, User, Stock, cmd, dmm


class MainServer(Server):
    def on_connect(self, client, address):
        try:
            usr = self.ask_client("[Internal] NSE_CLN_NK", client)
            
            if usr in users.keys():
                password = self.ask_client("[Internal] NSE_CLN_PW", client)

                if password == users[usr].password:
                    self.clients.append(client)
                    client.sendall("[Internal] CLN_JOINED".encode("utf-8"))

                    self.out(f"{usr} joined with IP address {address} and password '{password}'")
                else:
                    client.sendall("[Internal] INVALID_PW_ERR".encode("utf-8"))
                    self.out(f"user {usr} tried to log in with password '{password}' but failed")
            else:
                client.sendall("[Internal] IVALID_USR_ERR".encode("utf-8"))
                self.out(f"user {usr} tried to log in!")

            thread = threading.Thread(target=self.handle, args=(client, address, usr))
            thread.start()
        except Exception as e:
            self.out(f"\n\nServer Raised Exception\n\t{e}")


    def handle(self, client, address, name):
        self.names.append(name)

        while True:
            try:
                client.sendall("[Internal] CLN_INPUT".encode("utf-8"))
                message = client.recv(1024).decode("utf-8")

                if message in cmd.keys():
                    self.out(f"user {name} issued server command '{message}'")

                    try:
                        exec(compile(source=cmd[message], filename="command", mode="exec", optimize=1))
                    except Exception as e:
                        self.out(f"\n\nServer Raised Exception:\n\t{e}")
                else:
                    client.sendall("[Internal] INV_CMD_ERR".encode())
            except Exception as e:
                if client in self.clients:
                    self.clients.remove(client)
                    self.addresses.remove(address)
                    self.names.remove(name)

                self.out(f"\n\nServer Raised Exception:\n\t{e}")
                client.close()
                self.out(f"{name} lost connection")
                break


MainServer("25.80.62.167", 1989, "Main", True)
