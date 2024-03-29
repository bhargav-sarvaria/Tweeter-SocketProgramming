import socket
import json
import sys
import time
import threading

# arg1 -> Port to Send Messages
# arg2 -> Port to Receive Messages
# arg3 -> IP address of the Tracker process
# arg4 -> localIp address

# resp code 1 = Successful, 2 = Server Error, 3 = Bad Request, 4 = Internal Error
bufferSize = 1024
localIp = sys.argv[4] if len(sys.argv) > 4 else "127.0.0.1"
serverAddressPort = (sys.argv[3] if len(sys.argv) > 3 else '127.0.0.1', 17000)
encoding = 'utf-8'
# "10.120.70.117"
exitapp = False
LEFT_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 17001
RIGHT_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 17002
handle = ''

# Store state information for logical ring
neighbours = {}

# Create a UDP socket at client side
UDPClientSocketSend = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocketRcv = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocketRcv.settimeout(10)

UDPClientSocketSend.bind((localIp, LEFT_PORT))
UDPClientSocketRcv.bind((localIp, RIGHT_PORT))

# Send message to a process and return the response
def send_message(req, addr):
    resp = {}
    try:
        UDPClientSocketSend.sendto(json.dumps(req).encode(encoding), addr)
        bytesAddressPair = UDPClientSocketSend.recvfrom(bufferSize)
        resp = json.loads(bytesAddressPair[0].decode(encoding))
        print(json.dumps(resp, indent=2))
    except Exception as e:
        resp = {'code': 4, 'message' : 'Error while sending request to server'}
    return resp

# Listen to any requests on Right Port - Ex: setup logical ring, propogate tweet
def handle_incoming_messages():
    while (not exitapp):
        try:
            bytesAddressPair = UDPClientSocketRcv.recvfrom(bufferSize)
            message = json.loads(bytesAddressPair[0].decode(encoding))

            if message['type'] == 'setup':
                print(json.dumps(message, indent=2))
                neighbours[message['handle']] = message['data']
                resp = {'status': 1, 'type': 'setup'}
                UDPClientSocketSend.sendto(json.dumps(resp).encode(encoding), (message['rcv_ip'], message['rcv_port']))
            elif message['type'] == 'propogate_tweet':
                print(f"Received message from: {message['sender']}")
                if message['tweeter'] == handle:
                    # End Tweet logic here
                    print("End of logical ring and update the tracker")
                    request_obj = {'type': 'end-tweet', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle}

                    # Notifying server end of logical ring
                    UDPClientSocketSend.sendto(json.dumps(request_obj).encode(encoding), serverAddressPort)
                
                else:
                    print(f"@{message['tweeter']}: {message['tweet']}")
                    time.sleep(5)
                    req = {'type': 'propogate_tweet', 'sender': handle, 'tweeter': message['tweeter'], 'tweet': message['tweet'] }
                    send_to = neighbours[message['tweeter']]['rightNeighbour']
                    UDPClientSocketSend.sendto(json.dumps(req).encode(encoding), (
                        send_to['IP'], send_to['RIGHT_PORT']
                    ))

        except Exception as e:
            continue
            # print(e)


if __name__ == '__main__':
    while True:
        # Read the desired handle name from user
        handle = input('Enter a handle name to register:')
        data = {'handle' : handle, 'IP': localIp, 'LEFT_PORT': LEFT_PORT, 'RIGHT_PORT': RIGHT_PORT, 'followers': [], 'follows': []}
        request_obj = {'type': 'register', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'data': data }
        resp = send_message(request_obj, serverAddressPort)

        # If the handle name is registered successfully, start the application and read commands from user
        if resp['status'] == 1:
            break
    
    # Start a process to listen to any incoming messages on Right Port
    thread = threading.Thread(target=handle_incoming_messages)
    thread.start()

    while True:
        try:
            command = input('Enter a command:').split(' ')
            
            if command[0] == 'query' and command[1] == 'handles':
                request_obj = {'type': 'query_handles', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT }
                resp = send_message(request_obj, serverAddressPort)

            elif command[0] == 'follow':
                # Create and send request to follow a user
                to_follow = command[1][1:]
                if to_follow != handle:
                    request_obj = {'type': 'follow', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle, 'to_follow': to_follow }
                    resp = send_message(request_obj, serverAddressPort)
                else:
                    print('Cannot follow yourself!')
            
            elif command[0] == 'drop':
                # Create and send request to unfollow a user
                to_drop = command[1][1:]
                request_obj = {'type': 'drop', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle, 'to_drop': to_drop }
                resp = send_message(request_obj, serverAddressPort)
            
            elif command[0] == 'exit':
                # Break the loop to quit the application
                request_obj = {'type': 'exit', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle }
                resp = send_message(request_obj, serverAddressPort)
                exitapp = True
                break
            
            elif command[0] == 'tweet':
                tweet = command[1]
                request_obj = {'type': 'tweet', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle}
                resp = send_message(request_obj, serverAddressPort)

                if resp['status'] == 1:
                    followers = resp['followers']
                    total = len(followers)
                    if total > 1:
                        neighbours[handle] = {'leftNeighbour': followers[-1], 'rightNeighbour': followers[1]}
                        for idx, follower in enumerate(followers):
                            if idx == 0:
                                continue
                            leftNeighbour = followers[(idx - 1)%total]
                            rightNeighbour = followers[(idx + 1)%total]
                            request_obj = {'type': 'setup', 'rcv_ip': localIp, 'rcv_port': LEFT_PORT, 'handle': handle, 'data': {'leftNeighbour': leftNeighbour, 'rightNeighbour': rightNeighbour} }
                            resp = send_message(request_obj, (follower['IP'], follower['RIGHT_PORT']))
                            if resp['status'] != 1:
                                print('Error in creating logical ring!')
                                break
                        
                        req = {'type': 'propogate_tweet', 'sender': handle, 'tweeter': handle, 'tweet': tweet }
                        send_to = neighbours[handle]['rightNeighbour']
                        UDPClientSocketSend.sendto(json.dumps(req).encode(encoding), (
                            send_to['IP'], send_to['RIGHT_PORT']
                        ))

                        while True:
                            # Wait for response from server for status of propogating the tweet
                            bytesAddressPair = UDPClientSocketSend.recvfrom(bufferSize)
                            resp = json.loads(bytesAddressPair[0].decode(encoding))
                            
                            if resp['type'] == 'tweet':
                                print(resp['message'])
                                break
                        
            else:
                print('Invalid command')

        
        except Exception as e:
            print(e)

    thread.join()