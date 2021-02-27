from asciichartpy import plot


def wallet(client, username, stocks, users):
    from texttable import Texttable
    
    user              = users[username]
    usr_stocks        = user.portfolio
    total_stock_value = 0
    total_amount      = 0
    arr               = [["TICKER", "QUANTITÀ", "VALORE"]]

    table             = Texttable()
    table.set_cols_align(["l", "r", "r"])
    table.set_cols_valign(["m", "m", "m"])

    for index, stock in enumerate(usr_stocks.keys()):
        stock_name         = str(stock)
        stock_amount       = usr_stocks[stock_name]
        stock_value        = round(float(stocks[stock_name].price * stock_amount))
        increment          = float(((stocks[stock_name].price - stocks[stock_name].prec) / stocks[stock_name].prec) * 100)
        arr.append         ( [stock_name, f"{stock_amount:,}", f"{stock_value:,}"] )
        total_stock_value += stock_value
        total_amount      += stock_amount

    arr.append([f"Totale", f"{total_amount:,}", f"{total_stock_value:,}"])
    table.add_rows(arr)
    string = table.draw()
    string += f"\n\nSaldo carta: ${user.balance:,}\n"
    client.sendall(string.encode("utf-8"))


def sell(client, name, stocks, users, market, dmm):
    if len(market) <= 11:
        client.sendall("\nInserire ticker titolo\n".encode("utf-8"))
        client.sendall("[Internal] CLN_ASK".encode("utf-8"))
        stock      = client.recv(1024).decode("utf-8")
        usr_stocks = users[name].portfolio

        if stock in usr_stocks:
            _stock           = stocks[stock]
            stock_max_amount = usr_stocks[stock]

            client.sendall("\nInserire quantità di titoli da piazzare sul mercato\n".encode("utf-8"))
            client.sendall("[Internal] CLN_ASK".encode("utf-8"))
            stock_amount     = int(client.recv(1024).decode("utf-8"))

            if stock_amount <= stock_max_amount:
                client.sendall("\nSpecificare il prezzo di un singolo titolo\n".encode("utf-8"))
                client.sendall("[Internal] CLN_ASK".encode("utf-8"))
                stock_price  = float(client.recv(1024).decode("utf-8"))

                result = {
                    "name"  : stock,
                    "amount": stock_amount,
                    "price" : round(float(stock_price), 2),
                    "tot"   : round(int(stock_price * stock_amount)),
                    "seller": users[name].username
                }

                stocks[stock].exchange(users[name].username, dmm.username, stock_amount)

                client.sendall("\nTitolo piazzato sul mercato con successo\n".encode("utf-8"))
                return result
            else:
                client.sendall("\nNon possiedi la quantità specificata di titoli\n".encode("utf-8"))
                return False
        else:
            client.sendall("[Internal] INV_TICKER".encode("utf-8"))
            return False
    else:
        client.sendall("Il mercato è già pieno, devi acquistare qualcosa o aspettare che qualcuno lo faccia\n".encode("utf-8"))
        return False


def stock(client, stocks):
    from texttable import Texttable

    def sort(e):
        import backend.database as dbb
        return dbb.stocks[e].price * dbb.stocks[e].amount

    arr               =   [["TICKER", "PREZZO", "VALORE", "VARIAZIONE", "30 DAY", "IPO"]]
    table             =   Texttable()
    table.set_cols_align( ["l", "r", "r", "r", "r", "r"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m"])

    stocks_list = list(stocks.keys())
    stocks_list.sort(key=sort, reverse=True)

    for stock in stocks_list:
        stock_name         = str(stock)
        stock_value        = int(round(stocks[stock_name].price * stocks[stock].amount))
        increment          = round((stocks[stock].price - stocks[stock].prec) / stocks[stock].prec * 100, 2)
        month_increment    = round((stocks[stock].price - stocks[stock].month) / stocks[stock].month * 100, 2)
        ipo                = stocks[stock].ipo
        arr.append         ( [stock_name, f"{round(float(round(stock_value) / stocks[stock].amount), 2):.2f}", f"{round(stock_value):,}", f"{increment:+,.2f}%", f"{month_increment:+,.2f}%", f"{ipo:,}"])

    table.add_rows(arr)
    string = table.draw() + "\n"

    client.sendall(string.encode("utf-8"))


def buy(client, name, users, stocks, market, dmm):
    from texttable import Texttable

    arr               =   [["ID", "TICKER", "PREZZO", "QUANTITÀ", "TOTALE", "QUOTA"]]
    table             =   Texttable()
    table.set_cols_align( ["m", "l", "r", "r", "r", "r"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m"])

    for index, item in enumerate(market):
        stock_name   = item["name"]
        stock_seller = item["seller"]
        stock_amount = item["amount"]
        stock_price  = float(item["price"])
        stock_tot    = round(int(item["tot"]))
        steak        = round(stock_amount / stocks[stock_name].amount * 100, 4)

        arr.append([index, stock_name, f"{stock_price:,}", f"{stock_amount:,}", f"{stock_tot:,}", f"{steak}%"])

    table.add_rows(arr)
    string = table.draw() + "\n"
    string += "\n\nInserire l'ID del titolo che si vuole acquistare\n"

    client.sendall(string.encode("utf-8"))

    client.sendall("[Internal] CLN_ASK".encode("utf-8"))
    id = int(client.recv(1024).decode("utf-8"))

    if id < len(market):
        trade  = market[id]
        _name   = trade["name"]
        seller = trade["seller"]
        amount = trade["amount"]
        price  = round(float(trade["price"]), 3)
        tot    = int(trade["tot"])
        buyer  = users[name]

        if buyer.balance >= tot:
            stock  = stocks[_name]
            stock.exchange(dmm.username, name, amount)
            buyer.pay(seller, price * amount)

            commission = round(tot / 100 * 3)
            buyer.pay(dmm.username, commission)

            stocks[_name].price = price

            client.sendall("Transazione completata\n".encode("utf-8"))
            return id
        else:
            client.sendall("Non disponi di abbastanza soldi per poter effettuare la transazione\n".encode("utf-8"))
            return False
    else:
        client.sendall("ID non valido\n".encode("utf-8"))
        return False


def help(client):
    from texttable import Texttable

    arr               =   [["COMANDO", "SPIEGAZIONE", "SINTASSI"]]
    table             =   Texttable()
    table.set_cols_align( ["l", "l", "l"])
    table.set_cols_valign(["m", "m", "m"])

    commands = {
        "borsa"      : ["Permette di visualizzare l'attuale andamento dei mercati"       , "Nessun parametro"],
        "portafoglio": ["Permette di visualizzare le finanze private dell'account in uso", "Nessun parametro"],
        "vendi"      : ["Permette di vendere titoli"                                     , "Ticker del titolo, quantita' e prezzo per titolo"],
        "compra"     : ["Permette di acquistare titoli dal mercato"                      , "ID dell'ordine di vendita"],
        "aiuto"      : ["Mostra questa pagina"                                           , "Nessun parametro"],
        "paga"       : ["Permette di pagare direttamente ad una persona o società"       , "Destinatario, somma"]
    }

    for command in commands:
        arr.append([command, commands[command][0], commands[command][1]])

    table.add_rows(arr)


    string = f"""
Benvenuto nel centro di supporto MC Trader.
Qui puoi trovare informazioni sul funzionamento del programma e del mercato.

{table.draw()}

MERCATO:
Il mercato è un utilissimo strumento che permette di migliorare la produttività del server.
Permette alle società di finanziare i propri progetti e agli investitori di guadagnarci.
Il mercato del server è sicuro e robusto, anche in caso di perdita la maggior parte dei titoli sono garantiti o dallo Stato o da chi li emette.
"""

    client.sendall(string.encode("utf-8"))


def pay(client, name, users):
    client.sendall("Inserire il nome di chi si vuole pagare\n".encode("utf-8"))
    client.sendall("[Internal] CLN_ASK".encode("utf-8"))
    who = str(client.recv(1024).decode("utf-8"))

    if who not in users:
        client.sendall("Il nome specificato non esiste\n\n".encode("utf-8"))
        return False

    client.sendall("Specificare la dimensione della transazione\n".encode("utf-8"))
    client.sendall("[Internal] CLN_ASK".encode("utf-8"))
    payment = int(client.recv(1024).decode("utf-8"))

    try:
        if not float(payment) == payment:
            if not int(payment) == payment:
                client.sendall("La somma specificata non è valida\n".encode("utf-8"))
                return False
    except: 
        client.sendall("La somma specificata non è valida\n".encode("utf-8"))
        return False
    
    try:
        payer = users[name]
        payer.pay(who, payment)
        client.sendall("Transazione effettuata con successo!\n".encode("utf-8"))
        return True
    except: 
        client.sendall("Transazione fallita\n".encode("utf-8"))
        return False
