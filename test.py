import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 5001))

send = {
    "command": "GET_DATA",
    "request": "entities"
}

ss = str(send).encode("utf-8")

while True:
    client.send(ss)
    ans = client.recv(1024)
    print(ans)
