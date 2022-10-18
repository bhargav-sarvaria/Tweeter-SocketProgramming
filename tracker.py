import socket
import threading
import json
import sys
import copy
from xml.sax import handler

# arg1 -> Port for Tracker
# arg2 -> IP address of Tracker

localIP     = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
localPort   = int(sys.argv[1]) if len(sys.argv) > 1 else 17000
bufferSize  = 1024
encoding = 'utf-8'

# Database for storing information of Tweeter users
USERS = {}

# Create a UDP socket
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
        resp = drop(req)
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
    elif req['type'] == 'exit':
        exit(req)

def tweet(req):
    try:
        if req['handle'] in USERS:
            user = USERS[req['handle']]
            followers = user['followers']

            followers_arr = []
            followers_arr.append(user)
            for fol in followers:
                followers_arr.append(fol)

            resp = {'status': 1, 'type': 'tweet', 'count': len(followers_arr) - 1, 'followers': followers_arr}
            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
            return resp
        
        resp = {'status': 3, 'type': 'tweet', 'message': f"Handle {req['handle']} does not exist!"}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return resp
    except Exception as e:
        # print(e)
        resp = {'status': 2, 'type': 'tweet', 'message': 'Internal error in Tracker'}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return resp

def exit(req):
    if req['handle'] in USERS:
        user = USERS[req['handle']]
        for to_unfollow in user['follows']: 
            drop({'type': 'drop',  'handle': user['handle'], 'to_drop': to_unfollow })
    
        for user in user['followers']:
            follows = USERS[user['handle']]['follows']
            follows.remove(req['handle'])

    USERS.pop(req['handle'], None)
    resp = {'status': 1, 'type': 'exit', 'message': 'Deleted user successfully'}
    UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
    return 


def drop(req):
    try:
        if req['to_drop'] in USERS:
            user = USERS[req['to_drop']]
            followers = user['followers']
            if not any(u['handle'] == req['handle'] for u in followers):
                return {'status': 3, 'type': 'drop', 'message': f"Handle {req['handle']} does not exist in the followers list!"}
            followers[:] = [u for u in followers if u.get('handle') != req['handle']]
            followers = sorted(followers, key=lambda d: d['handle'])
            user['followers'] = followers
            return {'status': 1, 'type': 'drop', 'message': f"{req['handle']} is not following {req['to_drop']} anymore"}

        return {'status': 3, 'type': 'drop', 'message': f"Handle {req['to_drop']} does not exist!"}        
    except Exception as e:
        # print(e)
        return {'status': 2, 'type': 'drop', 'message': 'Internal error in Tracker'}

def follow(req):
    # Check if both the users exist and user1 is not following user2 already
    try:
        if req['handle'] in USERS:
            user = USERS[req['handle']]
            if req['to_follow'] in USERS:
                user['follows'].append(req['to_follow'])
                user = copy.deepcopy(user)
                user.pop('followers', None)
                user.pop('follows', None)
                to_follow = USERS[req['to_follow']]
                followers = to_follow['followers']
                followers.append(user)
                followers = sorted(followers, key=lambda d: d['handle'])
                to_follow['followers'] = copy.deepcopy(followers)
                # If it is a valid request return success
                resp = {'status': 1, 'type': 'follow', 'message': f"{req['handle']} is now following {req['to_follow']}"}
                UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                return
            else:
                # If the handle to follow does not exist return failure
                resp = {'status': 3, 'type': 'follow', 'message': f"Handle {req['to_follow']} does not exist!"}
                UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
                return
        else:
            # If the handle name of user process does not exist return failure``
            resp = {'status': 3, 'type': 'follow', 'message': f"Handle {req['handle']} does not exist!"}
            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
            return
        
    except Exception as e:
        # print(e)
        resp = {'status': 2, 'type': 'follow', 'message': 'Internal error in Tracker'}
        UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
        return

# Function to handle registeration of new users
def register_user(req):
    # Check if the IP and Port combination or the handle name already exists
    data = req['data']
    for handle in USERS:
        user = USERS[handle]
        if handle == data['handle']:
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

    # If it is a valid request return sucesss
    USERS[data['handle']] = data
    resp = {'status': 1, 'type': 'register', 'message': 'handle registered successfully'}  
    UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))

# Function to return the count and list of registered users
def query_handles(req):
    # Return the count and list of users
    resp = {'status': 1, 'type': 'query_handles', 'count': len(USERS.keys()), 'data': USERS}  
    UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (req['rcv_ip'], req['rcv_port']))
    return resp

# Listen for incoming datagrams
while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = json.loads(bytesAddressPair[0].decode(encoding))

        print(json.dumps(message, indent=2))

        address = bytesAddressPair[1]
        if message['type'] == 'tweet':
            resp = tweet(message)
            if resp['status'] == 1 and len(resp['followers']) > 1:
                while True:
                    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
                    req = json.loads(bytesAddressPair[0].decode(encoding))

                    if req['type'] == 'end-tweet':
                        if req['handle'] ==  message['handle']:
                            print('Successfully propogated tweet')
                            resp = {'status': 1, 'type': 'tweet', 'message': 'Success'}  
                            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (message['rcv_ip'], message['rcv_port']))
                        else:
                            print('Tweet Unsuccessful')
                            resp = {'status': 4, 'type': 'tweet', 'message': 'Failure'}  
                            UDPServerSocket.sendto(json.dumps(resp).encode(encoding), (message['rcv_ip'], message['rcv_port']))
                        break

            #     print(json.dumps(message, indent=2))
        else:
            threading.Thread(target=handle_client, args=(message,)).start()
    except Exception as e:
        print(e)