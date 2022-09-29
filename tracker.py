import socket
import threading
import json
import sys

# arg1 -> Port for Tracker
# arg2 -> IP address of Tracker

localIP     = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
localPort   = sys.argv[1] if len(sys.argv) > 1 else 17000
bufferSize  = 1024
encoding = 'utf-8'

# Database for storing information of Tweeter users
USERS = []

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

def handle_client(req):
    if req['type'] == 'register':
        register_user(req)
    elif req['type'] == 'query_handles':
        query_handles(req)
    elif req['type'] == 'follow':
        follow(req)
    elif req['type'] == 'drop':
        drop(req)

def tweet(req):
    try:
        for user in USERS:
            if user['handle'] == req['handle']:
                followers = user['followers']
                followers.insert(0, user)
                resp = {'status': 1, 'type': 'tweet', 'count': len(followers), 'followers': followers}
                UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                return resp
        
        resp = {'status': 3, 'type': 'tweet', 'message': f"Handle {req['handle']} does not exist!"}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return resp
    except Exception as e:
        print(e)
        resp = {'status': 2, 'type': 'follow', 'message': 'Internal error in Tracker'}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return resp

def drop(req):
    try:
        for idx, user in enumerate(USERS):
            if user['handle'] == req['to_drop']:
                followers = user['followers']
                if not any(u['handle'] == req['handle'] for u in followers):
                    resp = {'status': 3, 'type': 'drop', 'message': f"Handle {req['handle']} does not exist in the followers list!"}
                    UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                    return
                followers[:] = [u for u in followers if u.get('handle') != req['handle']]
                followers = sorted(followers, key=lambda d: d['handle'])
                user['followers'] = followers
                USERS[idx] = user
                print(json.dumps(USERS, indent=2))
                resp = {'status': 1, 'type': 'drop', 'message': f"{req['handle']} is not following {req['to_drop']} anymore"}
                UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                return

        resp = {'status': 3, 'type': 'follow', 'message': f"Handle {req['to_drop']} does not exist!"}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return
        
    except Exception as e:
        print(e)
        resp = {'status': 2, 'type': 'follow', 'message': 'Internal error in Tracker'}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return

def follow(req):
    try:
        for u in USERS:
            if u['handle'] == req['handle']:
                for idx, user in enumerate(USERS):
                    if user['handle'] == req['to_follow']:
                        followers = user['followers']
                        followers.append(u)
                        followers = sorted(followers, key=lambda d: d['handle'])
                        user['followers'] = followers
                        USERS[idx] = user
                        print(json.dumps(USERS, indent=2))
                        resp = {'status': 1, 'type': 'follow', 'message': f"{req['handle']} is now following {req['to_follow']}"}
                        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                        return

                resp = {'status': 3, 'type': 'follow', 'message': f"Handle {req['to_follow']} does not exist!"}
                UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                return

        resp = {'status': 3, 'type': 'follow', 'message': f"Handle {req['handle']} does not exist!"}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return
        
    except Exception as e:
        print(e)
        resp = {'status': 2, 'type': 'follow', 'message': 'Internal error in Tracker'}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return

# Function to handle registeration of new users
def register_user(req):
    data = req['data']
    for user in USERS:
        if user['handle'] == data['handle']:
            resp = {'status': 3, 'type': 'register', 'message': 'handle already exists'}
            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
            return
        if user['IP'] == data['IP'] and user['LEFT_PORT'] == data['LEFT_PORT']:
            resp = {'status': 3, 'type': 'register', 'message': 'Given host and port combination is already registered'}
            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
            return
        if user['IP'] == data['IP'] and user['RIGHT_PORT'] == data['RIGHT_PORT']:
            resp =  {'status': 3, 'type': 'register', 'message': 'Given host and port combination is already registered'}
            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
            return

    USERS.append(data)
    resp = {'status': 1, 'type': 'register', 'message': 'handle registered successfully'}  
    UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))

# Function to return the count and list of registered users
def query_handles(req):
    resp = {'status': 1, 'type': 'query_handles', 'count': len(USERS), 'data': USERS}  
    UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
    return resp

# Listen for incoming datagrams
while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = json.loads(bytesAddressPair[0].decode(encoding))
        address = bytesAddressPair[1]
        if message['type'] == 'tweet':
            resp = tweet(message)
            if resp['status'] == 1 and len(resp['followers']) > 1:
                bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
                message = json.loads(bytesAddressPair[0].decode(encoding))
        else:
            threading.Thread(target=handle_client, args=(message,)).start()
    except Exception as e:
        print(e)