

import socket
import threading
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT= 5566
ADDR=(IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "DISCONNECT!"

clients = []

def handle_client(conn, addr):
    print(f'\r[new connection] {addr} Connected!')
    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT)
        if msg == DISCONNECT_MSG:
            connected = False
        else:
            print(f"[{addr}] {msg}")
            f=open(msg, "w")
            conn.send("Message received and write the data into the text file ".encode(FORMAT))
            #conn.send("write the data into the text file".encode(FORMAT))
            msg1=conn.recv(1024).decode(FORMAT)
            f.write(msg1)
            conn.send("saved the text file".encode(FORMAT))
            f.close()
    conn.close()
            
            
    
def main():
    print(f'[SERVER] Starting... ')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f'[LISTENING] Server is listening on {IP}:{PORT}')
    while True:
        conn, addr = server.accept()
        clients.append({"c": conn, "address": addr})
        name=input("Enter the filename: ")
        conn.send(name.encode(FORMAT))
        msg=conn.recv(1024).decode(FORMAT)
        print(msg)
        f1=open(name, "r")
        msg3=f1.read()
        conn.send(msg3.encode(FORMAT))
        msg2=conn.recv(1024).decode(FORMAT)
        print(msg2) 
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()       
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
        
if __name__ == "__main__":
    main()