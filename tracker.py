import socket 
import threading
import json
import time

PORT = 17000
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

USERS = []

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = json.loads(conn.recv(1024).decode(FORMAT))
        if msg:
            print(f"[{addr}] {msg}")
            if msg['TYPE'] == 'register':
                resp = json.dumps(register_user(msg))
                conn.sendall(bytes(resp, encoding="utf-8"))
                connected = False
    conn.close()

def register_user(msg):
    for user in USERS:
        if user['HANDLE'] == msg['HANDLE']:
            return {'STATUS': 2, 'MSG': 'Handle already exists'}
        if user['IP'] == msg['IP'] and user['LEFT_PORT'] == msg['LEFT_PORT']:
            return {'STATUS': 2, 'MSG': 'Given host and port combination is already registered'}
        if user['IP'] == msg['IP'] and user['RIGHT_PORT'] == msg['RIGHT_PORT']:
            return {'STATUS': 2, 'MSG': 'Given host and port combination is already registered'}

    USERS.append(msg)
    return {'STATUS': 1, 'MSG': 'Handle registered successfully'}

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:

        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        time.sleep(20)
        # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()