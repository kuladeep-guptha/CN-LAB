
import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR0 = (IP, PORT)
ADDR1=(IP,5567)
ADDR2=(IP,5568)
ADDR3=(IP,5569)
ADDR4=(IP,5570)

SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def handle_server0(client0,client1,client2,client3,client4):
    connected = True
    while connected:
        msg = client0.recv(SIZE).decode(FORMAT)
        msg1=msg.split(':')
        if(msg1[0]=='k'):
            n=int(msg1[1])
            if(n==1):
                client1.send(msg.encode(FORMAT))
            if(n==2):
                client2.send(msg.encode(FORMAT))
            if(n==3):
                client3.send(msg.encode(FORMAT))
            if(n==4):
                client4.send(msg.encode(FORMAT))
            
        
        

def handle_server1(client0,client1,client2,client3,client4):
    connected = True
    while connected:
        msg = client1.recv(SIZE).decode(FORMAT)
        msg1=msg.split(':')
        if(msg1[0]=='k'):
            n=int(msg1[1])
            if(n==0):
                client0.send(msg.encode(FORMAT))
                msg3=client0.recv(SIZE).decode(FORMAT)
                client1.send(msg3.encode(FORMAT))
                
        

def handle_server2(client0,client1,client2,client3,client4):
    connected = True
    while connected:
        msg = client2.recv(SIZE).decode(FORMAT)
        msg1=msg.split(':')
        if(msg1[0]=='k'):
            n=int(msg1[1])
            if(n==0):
                client0.send(msg.encode(FORMAT))
                msg3=client0.recv(SIZE).decode(FORMAT)
                client2.send(msg3.encode(FORMAT))
        

def handle_server3(client0,client1,client2,client3,client4):
    connected = True
    while connected:
        msg = client3.recv(SIZE).decode(FORMAT)
        msg1=msg.split(':')
        if(msg1[0]=='k'):
            n=int(msg1[1])
            if(n==0):
                client0.send(msg.encode(FORMAT))
                msg3=client0.recv(SIZE).decode(FORMAT)
                client3.send(msg3.encode(FORMAT))
        

def handle_server4(client0,client1,client2,client3,client4):
    connected = True
    while connected:
        msg = client4.recv(SIZE).decode(FORMAT)
        msg1=msg.split(':')
        if(msg1[0]=='k'):
            n=int(msg1[1])
            if(n==0):
                client0.send(msg.encode(FORMAT))
                msg3=client0.recv(SIZE).decode(FORMAT)
                client4.send(msg3.encode(FORMAT))
        

        
    


        
        
def main():
    client0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client3=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client4=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    
    client0.connect(ADDR0)
    client1.connect(ADDR1)
    client2.connect(ADDR2)
    client3.connect(ADDR3)
    client4.connect(ADDR4)
    
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    # msg = input("> ")
    # client.send(msg.encode(FORMAT))
    msg = client0.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
    
    
    msg = client1.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
    
    msg = client2.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
    
    msg = client3.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
    
    msg = client4.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")
    
    
    
    
    
    
    
    thread1 = threading.Thread(target=handle_server0, args=(client0,client1,client2,client3,client4))
    thread1.start()
    
    thread1 = threading.Thread(target=handle_server1, args=(client0,client1,client2,client3,client4))
    thread1.start()
    
    thread1 = threading.Thread(target=handle_server2, args=(client0,client1,client2,client3,client4))
    thread1.start()
    
    thread1 = threading.Thread(target=handle_server3, args=(client0,client1,client2,client3,client4))
    thread1.start()
    
    thread1 = threading.Thread(target=handle_server4, args=(client0,client1,client2,client3,client4))
    thread1.start()
    
    
    
    
    
    

if __name__ == "__main__":
    main()