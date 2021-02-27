import threading
import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = ""
password = ""
last_seen = ""


server_codes = {
    "CLN_JOINED": """
import os
os.system("cls")

write_thread   = threading.Thread(target=write)
write_thread.start()
""",

    "INVALID_PW_ERR": """
print("Password non valida")
input()
client.close()
exit()
""",

    "IVALID_USR_ERR": """
print("Username non valido")
input()
client.close()
exit()
""",

    "INV_TICKER": """
print("Il ticker specificato e' inesistente o non e' contenuto nel tuo portafoglio")
""",

    "INV_CMD_ERR": """
print("Errore Locale")
print("-------------")
print("Il comando specificato è inesistente. Utilizza il comando 'aiuto' per ottenere una lista di comandi")
"""
}


try:
    client.connect(("25.80.62.167", 1989))
except Exception as e:
    print(e)
    input()
    exit()


def recieve(): 
    from time import sleep
    from datetime import datetime

    while True:
        try:
            message = client.recv(100_000).decode("utf-8")
            last_seen = datetime.now()

            if "[Internal] " in message:
                msg = message.replace("[Internal] ", "")

                if msg == "NSE_CLN_NK":
                    username = input("nome utente: ")
                    client.sendall(username.encode("utf-8"))
                elif msg == "NSE_CLN_PW":
                    password = input("password: ")
                    client.sendall(password.encode("utf-8"))
                elif msg in server_codes.keys():
                    exec(compile(server_codes[msg], "internal server order", "exec", optimize=1))
                else:
                    print(f"[Server] {msg}")
            else:
                print(message, end="")
        except Exception as e:
            import os
            from datetime import datetime
            os.system("cls")

            print(f"""
Python Recieve Excaption
------------------------
Si è verificato un errore durante la ricezione di dati dal server.
Questo potrebbe essere dovuto da un'interruzione nella connessione o da altri fattori. 


Resoconto
---------
Errore: Exception
Descrizione: {e}
Data: {datetime.now()}
Ultima connessione: {last_seen}

Cosa fare
---------
Almeno che l'errore non sia "Connessione interrotta forzatamente dall'host remoto" si chiede di inoltrare questo messaggio a tzyvoski!
            """)
            client.close()
            break


def write():
    from time import sleep
    from datetime import datetime
    import os

    while True:
        try:
            command = client.recv(128).decode("utf-8")
            
            if command== "[Internal] CLN_INPUT":
                message = input("> ")
                os.system("cls")
                client.sendall(message.replace("> ", "").encode("utf-8"))
            elif command == "[Internal] CLN_ASK":
                message = input("Risposta: ")
                client.sendall(message.encode("utf-8"))
        except:
            continue


import os
os.system("cls")
os.system("color 06")

recieve()
