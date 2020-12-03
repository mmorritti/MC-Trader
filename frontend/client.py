import threading
import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = ""
password = ""

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
"""
}


try:
    client.connect(("25.80.62.167", 1989))
except:
    input()
    exit()


def recieve():
    while True:
        try:
            message = client.recv(100_000).decode("utf-8")

            if "[Internal] " in message:
                msg = message.replace("[Internal] ", "")

                if msg == "NSE_CLN_NK":
                    username = input("nome utente: ")
                    client.send(username.encode("utf-8"))
                elif msg == "NSE_CLN_PW":
                    password = input("password: ")
                    client.send(password.encode("utf-8"))
                elif msg in server_codes.keys():
                    exec(compile(server_codes[msg], "internal server order", "exec", optimize=1))
                else:
                    print(f"[Server] {msg}")
            else:
                print(message)
        except:
            print("Qualcosa è andato storto durante uno scambio di informazioni tra server e client.")
            client.close()
            break

def write():
    while True:
        from time import sleep

        command = client.recv(128).decode("utf-8")

        sleep(0.010)
        if command== "[Internal] CLN_INPUT":
            message = input("> ")
            client.send(message.replace("> ", "").encode("utf-8"))
        elif command == "[Internal] CLN_ASK":
            message = input("Risposta: ")
            client.send(message.encode("utf-8"))


import os
os.system("cls")

recieve_thread = threading.Thread(target=recieve)
recieve_thread.start()
