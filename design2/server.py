import socket
import threading
import sys
import os

IP=socket.gethostbyname(socket.gethostname())
PORT=5566
ADDR=(IP,PORT)
SIZE=1024
FORMAT="utf-8"
DISCONNECT_MESSAGE='!DISCONNECT'

clients=[]
l1=[]

count=0

def search(conn):
    for i in range(len(l1)):
        if(l1[i]==conn):
            return 1
        else:
            return 0

def handle_client(conn,addr):
    print(f"\r[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
            for client in clients:
                if client["addr"] == addr:
                    clients.remove(client)
                    break
        else:
            print(msg)
            conn.send("Msg received".encode(FORMAT))
    
    conn.close() 
          

def main():
    print(f"[STATRING] server is starting")
    global count
    count=5
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] server is listening on {IP}:{PORT}")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    conn1,addr1=server.accept()
    conn1.send("MSG".encode(FORMAT))
    
    while True:
        conn,addr=server.accept()
        if(count>0 or len(clients)<5):
            clients.append({"c":conn,"addr":addr})
            l1.append(conn)
            count=count-1
            thread=threading.Thread(target=handle_client,args=(conn,addr))
            thread.start()
            print(f"\r[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
        else:
            if(search(conn)):
                count=count-1
            else:
                conn1.send("{conn}:{addr}".encode(FORMAT))
                print(conn1.recv(SIZE).decode(FORMAT))
                
            
        
    
    
    
    
    
    
    
    

if __name__=="__main__":
    main()