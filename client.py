import socket
import json
import sys
import threading

# arg1 -> Port to Send Messages
# arg2 -> Port to Receive Messages
# arg3 -> localIp address
# arg4 -> IP address of the Tracker process

# resp code 1 = Successful, 2 = Server Error, 3 = Bad Request, 4 = Internal Error

bufferSize = 1024
localIp = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
serverAddressPort = (sys.argv[4] if len(sys.argv) > 4 else localIp, 17000)
encoding = 'utf-8'
# "10.120.70.117"
LEFT_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 17001
RIGHT_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 17002
handle = ''
neighbours = {}

# Create a UDP socket at client side
UDPClientSocketSend = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocketRcv = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPClientSocketSend.bind((localIp, LEFT_PORT))
UDPClientSocketRcv.bind((localIp, RIGHT_PORT))

# Send to server using created UDP socket
def send_message(req, addr):
    resp = {}
    try:
        UDPClientSocketSend.sendto(json.dumps(req).encode(encoding), addr)
        bytesAddressPair = UDPClientSocketSend.recvfrom(bufferSize)
        resp = json.loads(bytesAddressPair[0].decode(encoding))
    except Exception as e:
        print(e)
        resp = {'code': 4, 'message' : 'Error while sending request to server'}
    return resp

def handle_incoming_messages():
    while(True):
        try:
            bytesAddressPair = UDPClientSocketRcv.recvfrom(bufferSize)
            message = json.loads(bytesAddressPair[0].decode(encoding))

            if message['type'] == 'setup':
                neighbours[message['handle']] = message['data']
                resp = {'status': 1, 'type': 'setup'}
                UDPClientSocketSend.sendto(json.dumps(resp).encode(encoding), (message['rcv_ip'], message['rcv_port']))
            elif message['type'] == 'propogate_tweet':
                if message['sender'] == handle:
                    # End Tweet logic here
                    return

                print(f"Received message from: {message['sender']}")
                print(f"@{message['tweeter']}: {message['tweet']}")
                req = {'type': 'propogate_tweet', 'sender': handle, 'tweeter': message['tweeter'], 'tweet': message['tweet'] }
                send_to = neighbours[handle]['rightNeighbour']
                UDPClientSocketSend.sendto(json.dumps(req).encode(encoding), (
                    send_to['IP'], send_to['RIGHT_PORT']
                ))

        except Exception as e:
            print(e)

if __name__ == '__main__':
    while True:
        handle = input('Enter a handle name to register:')
        data = {'handle' : handle, 'IP': localIp, 'LEFT_PORT': LEFT_PORT, 'RIGHT_PORT': RIGHT_PORT, 'followers': []}
        request_obj = {'type': 'register', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'data': data }
        resp = send_message(request_obj, serverAddressPort)
        print(resp['message'])
        if resp['status'] == 1:
            break
    
    threading.Thread(target=handle_incoming_messages).start()

    while True:
        try:
            command = input('Enter a command:').split(' ')
            if command[0] == 'query' and command[1] == 'handles':
                request_obj = {'type': 'query_handles', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'data': data }
                resp = send_message(request_obj, serverAddressPort)

                if resp['status'] == 1:
                    print(f"User Count: {resp['count']}")
                    print(json.dumps(resp['data'], indent=2))
                else:
                    print(resp['message'])
            elif command[0] == 'follow':
                to_follow = command[1][1:]
                request_obj = {'type': 'follow', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle, 'to_follow': to_follow }
                resp = send_message(request_obj, serverAddressPort)
                print(resp['message'])
            elif command[0] == 'drop':
                to_drop = command[1][1:]
                request_obj = {'type': 'drop', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle, 'to_drop': to_drop }
                resp = send_message(request_obj, serverAddressPort)
                print(resp['message'])
            elif command[0] == 'exit':
                print('Exiting the application!')
                break
            elif command[0] == 'tweet':
                tweet = command[1]
                request_obj = {'type': 'tweet', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle}
                resp = send_message(request_obj, serverAddressPort)

                if resp['status'] == 1:
                    followers = resp['followers']
                    total = len(followers)
                    if total > 1:
                        neighbours[handle] = {leftNeighbour, rightNeighbour}
                        for idx, follower in enumerate(followers[1:]):
                            leftNeighbour = followers[(idx - 1)%total]
                            rightNeighbour = followers[(idx + 1)%total]
                            request_obj = {'type': 'setup', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle, 'data': {leftNeighbour, rightNeighbour} }
                            resp = send_message(request_obj, (follower['IP'], follower['RIGHT_PORT']))
                            if resp['status'] != 1:
                                print('Error in creating logical ring!')
                                break
                        
                        req = {'type': 'propogate_tweet', 'sender': handle, 'tweeter': handle, 'tweet': tweet }
                        send_to = neighbours[handle]['rightNeighbour']
                        UDPClientSocketSend.sendto(json.dumps(req).encode(encoding), (
                            send_to['IP'], send_to['RIGHT_PORT']
                        ))
                        
            else:
                print('Invalid command')
        except Exception as e:
            print(e)