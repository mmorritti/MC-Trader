import threading
import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(("localhost", 2005))
except:
    print("Impossibile connettersi al server privato")
    input()


def recieve():
    while True:
        try:
            message = client.recv(1024).decode()

            print(message)
        except:
            print("Qualcosa è andato storto durante uno scambio di informazioni tra server e client.")
            client.close()
            break


def write():
    while True:
        message = input("> ")
        client.send(message.replace("> ", "").encode("utf-8"))


recieve_thread = threading.Thread(target=recieve)
recieve_thread.start()

write_thread  = threading.Thread(target=write)
write_thread.start()
