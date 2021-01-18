from backend.server_def import Server
import threading
import backend.commands as commands


class User:
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
        if who in users:
            reciever = users[who]
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
        seller = users[from_]
        buyer  = users[to_]

        if seller.remv(self.ticker, amount):
            buyer.add(self.ticker, amount)
            return True
        else:
            return False
        

users = {
    "tzyvoski"       : User("tzyvoski"      , "Almirox2005"  , 0.00000000000),
    "XfanX46"        : User("XfanX46"       , "xfanx"        , 0.00000000000),
    "Lory5"          : User("Lory5"         , "lroy"         , 0.00000000000),
    "Bazuks"         : User("Bazuks"        , "bazuks"       , 0.00000000000),
    "Rize"           : User("Rize"          , "rize"         , 0.00000000000),
    "Guggi17"        : User("Guggi17"       , "guggi17"      , 0.00000000000),
    "AndrySpartan"   : User("AndrySpartan"  , "andry"        , 0.00000000000),
    "iBlack_Jack_NS" : User("iBlack_Jack_NS", "blackjack"    , 0.00000000000),
    "tellmeCIRKE"    : User("tellmeCIRKE"   , "tellme"       , 0.00000000000),
    "Gock"           : User("Gock"          , "gock"         , 0.00000000000),
    "ABET"           : User("ABET"          , "Loryvoski2020", 0.00000000000),
    "NEXT"           : User("NEXT"          , "NGP 2020"     , 0.00000000000),
    "BBNK"           : User("BBNK"          , "Central2030"  , 0.00000000000),
    "NTHP"           : User("NTHP"          , "nether"       , 0.00000000000),
    "UNICEF"         : User("UNICEF"        , "unicef"       , 0.00000000000),
    "dmm"            : User("dmm"           , "dfdsfjasfjk"  , 0.00000000000)
}
dmm = users["dmm"]

stocks = {
    "ABET"  : Stock("ABET"  , 1.000, 1.000, 100000000.0),
    "NEXT"  : Stock("NEXT"  , 670.0, 603.6, 10000000.00),
    "BBNK"  : Stock("BBNK"  , 6.000, 6.000, 10000000.00),
    "NTHP"  : Stock("NTHP"  , 0.000, 0.000, 100000.0000),
    "RWAY"  : Stock("RWAY"  , 2.000, 2.000, 1036800.000),
    "TIME"  : Stock("TIME"  , 0.000, 0.000, 3000000.000),
}

database = {
    "users": users,
    "stocks"  : stocks,
    "dmm"     : dmm
}

market  = []

cmd = {
    "borsa": "commands.stock(client, stocks)",
    "portafoglio": "commands.wallet(client, name, stocks, users)",
    "vendi": """
r = commands.sell(client, name, stocks, users, market, dmm)
if r is not False:
    market.append(r)
""",
    "compra": """
r = commands.buy(client, name, users, stocks, market, dmm)
if r is not False:
    market.pop(r)
""",

    "aiuto": "commands.help(client)"
}


class Database(Server):
    def handle(self, client, address, name):
        self.names.append(name)

        while True:
            try:
                req = eval(client.recv(1024).decode("utf-8"))

                if req["command"] == "GET_DATA":
                    client.sendall(str(database[req["request"]]).encode("utf-8"))
            except Exception as e:
                if client in self.clients:
                    self.clients.remove(client)
                    self.addresses.remove(address)
                    self.names.remove(name)

                self.out(f"\n\nServer Raised Exception:\n{e}")
                client.close()
                break


db_server = Database(address="localhost", port=5001, name="Database", debug=True)


def saveall():
    import pickle

    db_server.out("About to save all data...")

    for User in users:
        for attr in ["password", "balance", "portfolio"]:
            try:
                attribute = getattr(users[User], attr)
                directory = f"saves\\users\\{users[User].username}\\{attr}.dat"

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
        pickle.dump(str(market), open("saves\\market.dat", "wb"))
    except:
        pass

    db_server.out("Saved all data")


def loadall():
    import pickle

    db_server.out("About to load data...")

    for User in users:
        for attr in ["password", "balance", "portfolio"]:
            try:
                directory = directory = f"saves\\users\\{users[User].username}\\{attr}.dat"
                attribute = pickle.load(open(directory, "rb"))
                setattr(users[User], attr, attribute)
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

    

    db_server.out("Loaded all data")


def load_market():
    import pickle

    db_server.out("About to load market data...")

    try:
        loaded = pickle.load(open("saves\\market.dat", "rb"))
        db_server.out("Loaded all market data")
        return eval(loaded)
    except:
        db_server.out("Failed to load market data!")
        return []


loadall()
market = load_market()
