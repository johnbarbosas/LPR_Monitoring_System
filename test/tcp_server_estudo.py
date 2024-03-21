import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# AF_INET => IPv4
# SOCK_STREAM => TCP

host = socket.gethostname()
port = 5000

s.bind((host,port))
s.listen(5)

print(f"Listening on {host}:{port}")

while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")
    msg = "Welcome to the server!"

    dados = clientsocket.recv(1024)
    print(f"Dados recebidos: {dados.decode('utf-8')}")

    '''
    msg = f'{len(msg):<{HEADERSIZE}}' + msg 
    clientsocket.send(bytes(msg, "utf-8"))

    while True:
        time.sleep(3)
        msg = f"The time is! {time.time()}"
        msg = f'{len(msg):<{HEADERSIZE}}' + msg
        clientsocket.send(bytes(msg, "utf-8"))
    '''
