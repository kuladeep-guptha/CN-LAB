import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
ADDR1=(IP,5567)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


def handle_server():
    clients=[1,2,3,4,5,6,7,8,9]
    for i in range(9):
        port=int(input(f"/renter the port number"))
        ADDR=(IP,port)
        clients[i]=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clients[i].connect(ADDR)
        msg = clients[i].recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            clients[i].close()
        
            
        
    
    


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    # server_thread = threading.Thread(target=handle_server, args=(client,))
    # server_thread.start()
    client1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect(ADDR1)
    connected = True
    thread=threading.Thread(target=handle_server,args=())
    thread.start()
    while connected:
        msg = input("> ")
        
        client.send(msg.encode(FORMAT))
        if msg == DISCONNECT_MESSAGE:
            connected = False
        msg = client.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        

    print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    client.close()
    os._exit(0) 
    
    
if __name__ == "__main__":
    main()