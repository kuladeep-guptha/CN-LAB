
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

def handle_server(client,client1):
    connected = True
    while connected:
        msg = client.recv(SIZE).decode(FORMAT)
        client1.send(msg.encode(FORMAT))
        client.send("sent to sr".encode(FORMAT))
        
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    client1.connect(ADDR1)
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    # msg = input("> ")
    # client.send(msg.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
   
    
    
    msg = client1.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
    
    
    
    thread1 = threading.Thread(target=handle_server, args=(client,client1))
    thread1.start()
    
    
    
    
    

if __name__ == "__main__":
    main()