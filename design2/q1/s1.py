import socket
import threading
import sys
import os

IP=socket.gethostbyname(socket.gethostname())
PORT=5567
ADDR=(IP,PORT)
SIZE=1024
FORMAT="utf-8"
DISCONNECT_MESSAGE='!DISCONNECT'

clients=[]

def search(conn):
    for client in clients:
        if(client["c"]==conn):
            return 1
        else:
            return 0


def handle_man(conn1,addr1,conn):
    while True:
        conn1.send("k:0:{conn}".encode(FORMAT))
        
        msg=conn1.recv(SIZE).decode(FORMAT)
        msg1=msg.split(":")
        if(msg1[0]=='a'):
            print(msg)
        elif(msg1[0]=='k'):
            for client in clients:
                if(client['c']==conn):
                    clients.remove(client)
                    print("cannot connect")
                    conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
                    conn.close()
                    break
        elif(msg1[0]=='l'):
            if(msg1[1]=='yes'):
                for client in clients:
                    if(client['c']==conn):
                        clients.remove(client)
                        conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
                        conn.close()
                        break
            
            
        
        

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
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] server is listening on {IP}:{PORT}")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    conn1,addr1=server.accept()
    conn1.send("MSG1".encode(FORMAT))
    
    
    while True:
        
        conn,addr=server.accept()
        clients.append({"c":conn,"addr":addr})
        thread=threading.Thread(target=handle_man,args=(conn1,addr1,conn))
        thread.start()
        thread=threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()
        print(f"\r[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        
                
            
        
    
    
    
    
    
    
    
    

if __name__=="__main__":
    main()