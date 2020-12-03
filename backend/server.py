import threading
import socket
import commands


# Minecraft


class Entity:
    def __init__(self, username, password, bal):
        self.username  = str(username)
        self.password  = str(password)
        self.balance   = float(bal)
        self.portfolio = {}


    def remv(self, stock, amount):
        if stock in self.portfolio:
            if self.portfolio[stock] > int(amount):
                self.portfolio.__setitem__(stock, self.portfolio[stock] - int(amount))
                return True
            elif self.portfolio[stock] == amount:
                self.portfolio.pop(stock)
                return True
            else:
                return False
        else:
            return False


    def add(self, stock, amount):
        if stock in self.portfolio:
            self.portfolio.__setitem__(stock, self.portfolio[stock] + int(amount))
            return True
        else:
            self.portfolio.__setitem__(stock, int(amount))
            return True


    def pay(self, who, amount):
        if who in entities:
            reciever = entities[who]
            reciever.balance  += float(amount)
            self.balance -= float(amount)
            return True
        else:
            return False


class Stock:
    def __init__(self, ticker, price, prec, amount):
        self.ticker = str(ticker)
        self.price  = float(price)
        self.amount = int(amount)
        self.prec   = float(prec)
        self.month  = 1
        self.ipo    = 1


    def exchange(self, from_, to_, amount):
        seller = entities[from_]
        buyer  = entities[to_]

        if seller.remv(self.ticker, amount):
            buyer.add(self.ticker, amount)
            return True
        else:
            return False
        

entities = {
    "tzyvoski"       : Entity("tzyvoski"      , "Almirox2005"  , 0.00000000000),
    "XfanX46"        : Entity("XfanX46"       , "xfanx"        , 0.00000000000),
    "Lory5"          : Entity("Lory5"         , "lroy"         , 0.00000000000),
    "Bazuks"         : Entity("Bazuks"        , "bazuks"       , 0.00000000000),
    "Rize"           : Entity("Rize"          , "rize"         , 0.00000000000),
    "Guggi17"        : Entity("Guggi17"       , "guggi17"      , 0.00000000000),
    "ABET.NSE"       : Entity("ABET.NSE"      , "Loryvoski2020", 0.00000000000),
    "NGP.NSE"        : Entity("NGP.NSE"       , "NGP 2020"     , 0.00000000000),
    "BBNK.NSE"       : Entity("BBNK.NSE"      , "Central2030"  , 0.00000000000),
    "UNICEF"         : Entity("UNICEF"        , "unicef"       , 0.00000000000),
    "testuser0"      : Entity("testuser0"     , "password1"    , 0.00000000000),
    "dmm"            : Entity("dmm"           , "dfdsfjasfjk"  , 0.00000000000)
}
dmm = entities["dmm"]

stocks = {
    "ABET.NSE": Stock("ABET.NSE", 1.000, 1.000, 100000000.0),
    "NGP.NSE" : Stock("NGP.NSE" , 670.0, 603.6, 10000000.00),
    "BBNK.NSE": Stock("BBNK.NSE", 6.000, 6.000, 10000000.00),
}

# Public Server
host = "25.80.62.167"
port = 1989
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()


# Private server
private_host    = "localhost"
private_port    = 2005
private_server  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
private_server.bind((private_host, private_port))
private_server.listen()


clients = []
market  = []
cmd = {
    "borsa": "commands.stock(client, stocks)",
    "portafoglio": "commands.wallet(client, name, stocks, entities)",

    "vendi": """
r = commands.sell(client, name, stocks, entities, dmm)
if r is not (False or None):
    market.append(r)
""",

    "compra": """
r = commands.buy(client, name, entities, stocks, market, dmm)
if r is not False:
    market.pop(r)
"""
}


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client, address, name):
    while True:
        try:
            client.send("[Internal] CLN_INPUT".encode("utf-8"))
            message = client.recv(1024).decode("utf-8")
                
            if message in cmd.keys():
                exec(compile(source=cmd[message], filename="command", mode="exec", optimize=1))
                print(f"user {name} issued server command '{message}''")
            else:
                client.send("[Internal] INV_CMD_ERR".encode()) # Send an "Invalid Command Exception" to the client
        except Exception as e:
            if client in clients:
                clients.remove(client)

            client.close()
            print(f"{name} left")
            break


def private_handle(console, address):
    while True:
        try:
            message = console.recv(1024).decode()

            try:
                exec(compile(source=message, filename="order", mode="exec", optimize=1))
            except Exception as e:
                console.send(str(e).encode())
        except:
            clients.remove(console)
            console.close()
            print("lost cnnection from console!")
            break


def login(client, address):
    try:
        client.send("[Internal] NSE_CLN_NK".encode("utf-8"))
        usr = client.recv(1024).decode("utf-8")

        if usr in entities.keys():
            print(f"{usr} is logging in.")
            
            client.send("[Internal] NSE_CLN_PW".encode("utf-8"))
            password = client.recv(1024).decode("utf-8")

            if password == entities[usr].password:
                clients.append(client)
                client.send("[Internal] CLN_JOINED".encode("utf-8"))
                    
                print(f"user {usr} logged in with IP address '{address}' and password '{password}'.")
                print(f"{usr} joined")
            else:
                client.send("[Internal] INVALID_PW_ERR".encode("utf-8"))
                print(f"user {usr} tried to log in with password {password} but failed.")
        else:
            client.send("[Internal] IVALID_USR_ERR".encode("utf-8"))
            print(f"user {usr} tried to log in!")

        thread = threading.Thread(target=handle, args=(client, address, usr))
        thread.start()
    except:
        print("Something went wrong")


def main():
    while True:
        try:
            client, address = server.accept()
            print(f"{str(address)} is now connected to the server")
            
            login_thread = threading.Thread(target=login, args=(client, address))
            login_thread.start()
        except:
            print("Something went wrong")
            continue


def private_main():
    while True:
        console, address = private_server.accept()
        print("Console online!")
        console.send("Hello console!".encode())
        clients.append(console)
        commands.stock(console, stocks)

        private_thread = threading.Thread(target=private_handle, args=(console, address))
        private_thread.start()

        try:
            pass
        except:
            print("Connection Lost")
            continue


def saveall():
    import pickle

    for entity in entities:
        for attr in ["password", "balance", "portfolio"]:
            try:
                attribute = getattr(entities[entity], attr)
                directory = f"saves\\entities\\{entities[entity].username}\\{attr}.dat"

                pickle.dump(attribute, open(directory, "wb"))
            except:
                continue

    for stock in stocks:
        for attr in ["price", "amount", "prec", "month", "ipo"]:
            try:
                attribute = getattr(stocks[stock], attr)
                directory = f"saves\\stocks\\{stocks[stock].ticker}\\{attr}.dat"

                pickle.dump(attribute, open(directory, "wb"))
            except:
                continue

    try:
        pickle.dump(market, open("saves\\market.dat", "wb"))
    except:
        pass


def loadall():
    import pickle

    for entity in entities:
        for attr in ["password", "balance", "portfolio"]:
            try:
                directory = directory = f"saves\\entities\\{entities[entity].username}\\{attr}.dat"
                attribute = pickle.load(open(directory, "rb"))
                setattr(entities[entity], attr, attribute)
            except:
                continue


    for stock in stocks:
        for attr in ["price", "amount", "prec", "month", "ipo"]:
            try:
                directory = f"saves\\stocks\\{stocks[stock].ticker}\\{attr}.dat"
                attribute = pickle.load(open(directory, "rb"))
                setattr(stocks[stock], attr, attribute)
            except:
                continue

    try:
        market = pickle.load(open("saves\\market.dat", "rb"))
    except:
        pass


def init_session():
    for stock in stocks.keys():
        stocks[stock].prec = stock[stock].price
    
    saveall()


print("Server is starting. Please wait...")
loadall()

private_main_thread = threading.Thread(target=private_main)
private_main_thread.start()

main()
