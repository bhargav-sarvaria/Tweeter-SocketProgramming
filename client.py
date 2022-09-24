import socket
import json
import sys
from tkinter import RIGHT
from turtle import right
from unicodedata import name

HEADER = 64
SYS_IP = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '127.0.0.1'
SERVER_PORT = 17000
LEFT_PORT = 17001
RIGHT_PORT = 17002

def register(msg, server, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ADDR = (server, port)
        conn.bind((SYS_IP, LEFT_PORT))
        conn.connect(ADDR)
        conn.sendall(bytes(msg, encoding="utf-8"))
        resp = json.loads(conn.recv(2048).decode(FORMAT))
        print(resp['MSG'])
    finally:
        conn.close()

def isgoodipv4(s):
    pieces = s.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False

if __name__ == '__main__':
    
    # We input the Server IP address from user and 
    while SERVER == '':
        SERVER = input('Enter the IP address of Tracker:')
        if( not isgoodipv4(SERVER)): 
            SERVER = ''
            print("[ERROR] Please enter a valid IP address")

    while SERVER_PORT == 0:
        SERVER_PORT = input('Enter the Server\'s Port Number:')
        if(not SERVER_PORT.isdigit() or int(SERVER_PORT) not in range(17000,17500)): 
            SERVER_PORT = 0
            print("[ERROR] Please enter a valid Port # : Allowed Range: 17000 - 17499")
        else:
            SERVER_PORT = int(SERVER_PORT)
    
    while LEFT_PORT == 0:
        LEFT_PORT = input('Enter the Left Port Number:')
        if(not LEFT_PORT.isdigit() or int(LEFT_PORT) not in range(17000,17500)): 
            LEFT_PORT = 0
            print("[ERROR] Please enter a valid Port # : Allowed Range: 17000 - 17499 :")
        elif socket.gethostbyname(socket.gethostname()) == SERVER and int(LEFT_PORT) == SERVER_PORT:
            LEFT_PORT = 0
            print("[ERROR] Please enter a valid Port # : Given Port is already occupied by Server")
        else:
            LEFT_PORT = int(LEFT_PORT)

    while RIGHT_PORT == 0:
        RIGHT_PORT = input('Enter the Right Port Number:')
        if(not RIGHT_PORT.isdigit() or int(RIGHT_PORT) not in range(17000,17500) or int(RIGHT_PORT) == LEFT_PORT): 
            RIGHT_PORT = 0
            print("[ERROR] Please enter a valid Port # : Allowed Range: 17000 - 17499 : Value cannot be equal to Left Port #")
        elif socket.gethostbyname(socket.gethostname()) == SERVER and int(RIGHT_PORT) == SERVER_PORT:
            RIGHT_PORT = 0
            print("[ERROR] Please enter a valid Port # : Given Port is already occupied by Server")
        else:
            RIGHT_PORT = int(RIGHT_PORT)

    while True:
        command = input('Enter a command:').split(' ')

        if command[0] == 'register':
            handle = command[1][1:]
            msg = {'TYPE': 'register', 'HANDLE' : handle, 'IP': SYS_IP, 'LEFT_PORT': LEFT_PORT, 'RIGHT_PORT': RIGHT_PORT}
            register(json.dumps(msg), SERVER, SERVER_PORT)

        else:
            print('Invalid command')


    

