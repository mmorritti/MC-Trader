from asciichartpy import plot


def wallet(client, username, stocks, entities):
    from texttable import Texttable
    
    user              = entities[username]
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
    client.send(string.encode("utf-8"))


def sell(client, name, stocks, entities, dmm):
    client.send("\nInserire ticker titolo".encode("utf-8"))
    client.send("[Internal] CLN_ASK".encode("utf-8"))
    stock      = client.recv(1024).decode("utf-8")
    usr_stocks = entities[name].portfolio

    if stock in usr_stocks:
        _stock           = stocks[stock]
        stock_max_amount = usr_stocks[stock]

        client.send("\nInserire quantità di titoli da piazzare sul mercato".encode("utf-8"))
        client.send("[Internal] CLN_ASK".encode("utf-8"))
        stock_amount     = int(client.recv(1024).decode("utf-8"))

        if stock_amount <= stock_max_amount:
            client.send("\nSpecificare il prezzo di un singolo titolo".encode("utf-8"))
            client.send("[Internal] CLN_ASK".encode("utf-8"))
            stock_price  = float(client.recv(1024).decode("utf-8"))

            result = {
                "name"  : stock,
                "amount": stock_amount,
                "price" : stock_price,
                "tot"   : float(stock_price * stock_amount),
                "seller": entities[name].username
            }

            stocks[stock].exchange(entities[name].username, dmm.username, stock_amount)

            client.send("\nTitolo piazzato sul mercato con successo".encode("utf-8"))
            return result
        else:
            client.send("\nNon possiedi la quantità specificata di titoli".encode("utf-8"))
            return False
    else:
        client.send("[Internal] INV_TICKER".encode("utf-8"))
        return False


def stock(client, stocks):
    from texttable import Texttable

    arr               =   [["N.", "TICKER", "PREZZO", "CAPITALE", "INCREMENTO", "30 DAY", "IPO"]]
    table             =   Texttable()
    table.set_cols_align( ["m", "l", "r", "r", "r", "r", "r"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m"])

    for index, stock in enumerate(stocks.keys()):
        stock_name         = str(stock)
        stock_value        = int(stocks[stock_name].price * stocks[stock].amount)
        increment          = round((stocks[stock].price - stocks[stock].prec) / stocks[stock].prec * 100, 2)
        month_increment    = round((stocks[stock].price - stocks[stock].month) / stocks[stock].month * 100, 2)
        ipo                = stocks[stock].ipo
        arr.append         ( [index + 1, stock_name, f"{stocks[stock].price:,}", f"{stock_value:,}", f"{increment:,}%", f"{month_increment:,}%", f"{ipo:,}"])

    table.add_rows(arr)
    string = table.draw()

    client.send(string.encode("utf-8"))


def buy(client, name, entities, stocks, market, dmm):
    from texttable import Texttable

    arr               =   [["ID", "TICKER", "PREZZO", "QUANTITÀ", "QUOTA"]]
    table             =   Texttable()
    table.set_cols_align( ["m", "l", "r", "r", "r"])
    table.set_cols_valign(["m", "m", "m", "m", "m"])

    for index, item in enumerate(market):
        stock_name   = item["name"]
        stock_seller = item["seller"]
        stock_amount = item["amount"]
        stock_price  = item["price"]
        stock_tot    = item["tot"]
        steak        = round(stock_amount / stocks[stock_name].amount * 100, 4)

        arr.append([index, stock_name, f"{stock_price:,}", f"{stock_amount:,}", f"{steak}%"])

    table.add_rows(arr)
    string = table.draw() + "\n"
    string += "\n\nInserire l'ID del titolo che si vuole acquistare"

    client.send(string.encode("utf-8"))

    client.send("[Internal] CLN_ASK".encode("utf-8"))
    id = int(client.recv(1024).decode("utf-8"))

    if id < len(market):
        trade  = market[id]
        _name   = trade["name"]
        seller = trade["seller"]
        amount = trade["amount"]
        price  = trade["price"]
        tot    = trade["tot"]
        buyer  = entities[name]

        if buyer.balance >= tot:
            stock  = stocks[_name]
            stock.exchange(dmm.username, name, amount)
            buyer.pay(seller, tot)

            commission = float(tot / 100 * 3)
            buyer.pay(dmm.username, commission)

            stocks[_name].price = price

            client.send("Transazione completata".encode("utf-8"))
            return id
        else:
            client.send("Non disponi di abbastanza soldi per poter effettuare la transazione".encode("utf-8"))
            return False
    else:
        client.send("ID non valido".encode("utf-8"))
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

    client.send(string.encode("utf-8"))
