
import socket
import threading
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = ("192.168.137.66", PORT)
size = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"

def handle_server(client):
    file=client.recv(size).decode(FORMAT)
    fp=open(file, "w")
    client.send("[client] File opened".encode(FORMAT))
    data=client.recv(size).decode(FORMAT)
    fp.write(data)
    client.send("[client] File written".encode(FORMAT))
    fp.close()
    


def main():
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f'[CONNECTED] Connected to server on {IP} : {PORT}')
    connected=True
    
    while connected:
        msg=input("> Enter the filename: ")
        f1=open(msg, "r")
        if(f1==None):
            print("File not found")
            break
        
        client.send(msg.encode(FORMAT))
        msg1=client.recv(1024).decode(FORMAT)
        print(f"[SERVER]... {msg1}")
        msg2=f1.read()
        client.send(msg2.encode(FORMAT))
        msg3=client.recv(1024).decode(FORMAT)
        print(f"[SERVER]... {msg3}")
        if msg == DISCONNECT_MESSAGE:
            connected = False
    print(f'[DISCONNECTED].. Disconnected from {IP} : {PORT}')
    
    client.close()

if __name__ == '__main__':
    main()