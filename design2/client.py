import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
   

    # server_thread = threading.Thread(target=handle_server, args=(client,))
    # server_thread.start()

    connected = True
    while connected:
        msg = input("> ")
        client.send(msg.encode(FORMAT))
        if msg == DISCONNECT_MESSAGE:
            connected = False
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER] {msg}")

    print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    client.close()
    os._exit(0) 
    
    
if __name__ == "__main__":
    main()