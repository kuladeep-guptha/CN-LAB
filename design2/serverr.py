import socket
import threading
import sys

IP=socket.gethostbyname(socket.gethostname())
PORT=5567
ADDR=(IP,PORT)
SIZE=1024
FORMAT="utf-8"
DISCONNECT_MESSAGE='!DISCONNECT'

clients=[]
def handle_man(conn1,addr1):
    connected = True
    while connected:
        msg = conn1.recv(SIZE).decode(FORMAT)
        conn=msg.split(":")[0]
        addr=msg.split(":")[1]
        clients.append({"conn": conn, "addr": addr})
        print(f"\r[NEW CONNECTION] {addr} connected.")
        

def main():
    print(f"[STATRING] server is starting")
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] server is listening on {IP}:{PORT}")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    conn1,addr1=server.accept()
    conn1.send("MSG1".encode(FORMAT))
    
    thread = threading.Thread(target=handle_man, args=(conn1, addr1))
    thread.start()
    
    
    
    
    
    

if __name__=="__main__":
    main()