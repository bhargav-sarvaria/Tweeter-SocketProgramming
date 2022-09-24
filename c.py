from calendar import c
import socket
import json

HEADER = 64
SERVER_PORT = 17000
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"
ADDR = (SERVER, SERVER_PORT)
SYS_IP = socket.gethostbyname(socket.gethostname())
LEFT_PORT = 17001
RIGHT_PORT = 17002

def send_message(msg, server, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.bind((SYS_IP, LEFT_PORT))
        client_socket.connect((server, port))
        message = msg.encode(FORMAT)
        client_socket.send(message)
        resp = json.loads(client_socket.recv(1024).decode(FORMAT))
        # client_socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print(e)
        resp = {'status': 3, 'message': 'Internal error'}
    finally:
        client_socket.close()
    return resp

if __name__ == '__main__':
    while True:
        command = input('Enter a command:').split(' ')
        if command[0] == 'register':
            handle = command[1][1:]
            msg = {'TYPE': 'register', 'HANDLE' : handle, 'IP': SYS_IP, 'LEFT_PORT': LEFT_PORT, 'RIGHT_PORT': RIGHT_PORT}
            resp = send_message(json.dumps(msg), SERVER, SERVER_PORT)
            print(resp['message'])
        elif command[0] == 'query' and command[1] == 'handles':
            msg = {'TYPE': 'query_handles'}
            resp = send_message(json.dumps(msg), SERVER, SERVER_PORT)
            print(resp['data'])
        else:
            print('Invalid command')