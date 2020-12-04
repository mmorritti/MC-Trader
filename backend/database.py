from backend.server_def import Server
import threading
import backend.commands as commands


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
    "AndrySpartan"   : Entity("AndrySpartan"  , "andry"        , 0.00000000000),
    "iBlack_Jack_NS" : Entity("iBlack_Jack_NS", "blackjack"    , 0.00000000000),
    "tellmeCIRKE"    : Entity("tellmeCIRKE"   , "tellme"       , 0.00000000000),
    "ABET.NSE"       : Entity("ABET.NSE"      , "Loryvoski2020", 0.00000000000),
    "NGP.NSE"        : Entity("NGP.NSE"       , "NGP 2020"     , 0.00000000000),
    "BBNK.NSE"       : Entity("BBNK.NSE"      , "Central2030"  , 0.00000000000),
    "NETHP.NSE"      : Entity("NETHP.NSE"     , "nether"       , 0.00000000000),
    "UNICEF"         : Entity("UNICEF"        , "unicef"       , 0.00000000000),
    "testuser0"      : Entity("testuser0"     , "password1"    , 0.00000000000),
    "dmm"            : Entity("dmm"           , "dfdsfjasfjk"  , 0.00000000000)
}
dmm = entities["dmm"]

stocks = {
    "ABET.NSE" : Stock("ABET.NSE" , 1.000, 1.000, 100000000.0),
    "NGP.NSE"  : Stock("NGP.NSE"  , 670.0, 603.6, 10000000.00),
    "BBNK.NSE" : Stock("BBNK.NSE" , 6.000, 6.000, 10000000.00),
    "NETHP.NSE": Stock("NETHP.NSE", 0.000, 0.000, 100000.0000),
}

database = {
    "entities": entities,
    "stocks"  : stocks,
    "dmm"     : dmm
}

market  = []

cmd = {
    "borsa": "commands.stock(client, stocks)",
    "portafoglio": "commands.wallet(client, name, stocks, entities)",
    "vendi": """
r = commands.sell(client, name, stocks, entities, dmm)
if r is not False:
    market.append(r)
""",
    "compra": """
r = commands.buy(client, name, entities, stocks, market, dmm)
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
                    client.send(str(database[req["request"]]).encode("utf-8"))
            except Exception as e:
                if client in self.clients:
                    self.clients.remove(client)
                    self.addresses.remove(address)
                    self.names.remove(name)

                self.out(f"\n\nServer Raised Exception:\n{e}")
                client.close()
                break


db_server = Database(address="localhost", port=5001)


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


loadall()
