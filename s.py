from email import message
import socket 
import threading
import json

HEADER = 64
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
    try:
        msg = json.loads(conn.recv(1024).decode(FORMAT))
        print(f"[{addr}] {msg}")

        if msg['TYPE'] == 'register':
            message = json.dumps(register_user(msg))
        elif msg['TYPE'] == 'query_handles':
            message = json.dumps(query_handles(msg))
        conn.send(message.encode(FORMAT))
        test = conn.recv(1024).decode(FORMAT)
    except:
        conn.send(json.dumps({'status': 2, 'message': 'Invalid Request'}).encode(FORMAT))
    # finally:
    #     conn.shutdown()
    #     conn.close()

def query_handles():
    resp = {}
    resp['count'] = len(USERS)
    resp['data'] = USERS
    return resp


def register_user(msg):
    for user in USERS:
        if user['HANDLE'] == msg['HANDLE']:
            return {'STATUS': 2, 'message': 'Handle already exists'}
        if user['IP'] == msg['IP'] and user['LEFT_PORT'] == msg['LEFT_PORT']:
            return {'STATUS': 2, 'message': 'Given host and port combination is already registered'}
        if user['IP'] == msg['IP'] and user['RIGHT_PORT'] == msg['RIGHT_PORT']:
            return {'STATUS': 2, 'message': 'Given host and port combination is already registered'}

    USERS.append(msg)
    return {'STATUS': 1, 'message': 'Handle registered successfully'}     

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")
start()