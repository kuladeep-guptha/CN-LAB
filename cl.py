# import socket
# import threading

# #IP = socket.gethostbyname(socket.gethostname())
# host=socket.gethostname()
# port = 5566
# IP = "192.168.137.234"
# disconnect_msg = "!DISCONNECT"
# def main():
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         client.connect((IP, port))
#         client_id = input("Enter your unique identifier:")
#         client.send(client_id.encode())
#         print(f"successfully connected to the server at {IP} {port}")
#     except:
#         print(f"Unable to connect to server  {port}")
#     connected = True
#     while connected:
#         msg = input("Enter a msg to send to server")
#         client.send(msg.encode("utf-8"))
#         if msg == disconnect_msg:
#             connected = False
#         else:
#             msg = client.recv(1024).decode("utf-8")
#             print(f"[server] {msg}")
    

# if __name__ == '__main__':
#     main()

import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = ('172.16.18.76', PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def main(): 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    connected = True
    while connected:
        msg = input("> ")

        client.send(msg.encode(FORMAT))

        if msg == DISCONNECT_MSG:
            connected = False
        else:
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")

if __name__=="__main__":
    main()
    
    #Different types of topologies:
# 1)bus topology
# 2)ring topology
# 3)mesh topology
# 4)star topology
# 5)hybrid topology

# Bus topology:
# Advantages:
# 1)	Very cheaper when compared to other topology
# 2)	Since the nodes are connected linearly, if any node fails it doesnot effect the other nodes
# DisAdvantages:
# 1)    When the number of nodes increases the performance decreases
# 2)    If the main cable fails then the entire network fails
# 3)    The length of the cable is limited
# 4)    The data transfer rate is limited
# 5)    The security is very less
# ring topology:
# Advantages:
# 1)    The data transfer rate is very high
# 2)    The performance is very high
# 3)    The length of the cable is limited
# 4)    The security is very less
# DisAdvantages:
# 1)    If any node fails then the entire network fails
# 2)    The number of nodes that can be connected is limited
# 3)    The cost is very high
# 4)    The installation is very difficult
# 5)    The maintenance is very difficult
# mesh topology:
# Advantages:
# 1)    The data transfer rate is very high
# 2)    The performance is very high
# 3)    The length of the cable is limited
# 4)    The security is very high
# DisAdvantages:
# 1)    The cost is very high
# 2)    The installation is very difficult
# 3)    The maintenance is very difficult
# 4)    The number of nodes that can be connected is limited
# 5)    The number of cables required is very high




