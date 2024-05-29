import socket
import threading
import sys


IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "DISCONNECT!"

clients = []

def handle_client(conn, addr):
    print(f'\r[new connection] {addr} Connected!')
    for client in clients:
        if client['address'] != addr:
            conn.send(f"[new connection]... {client['address'][0]} {client['address'][1]} connected to the server".encode(FORMAT))
    for client in clients:
        if client['address'] != addr:
            client['c'].send(f"\n[already connected devices]...{addr[0]} {addr[1]}".encode(FORMAT))
    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT)
        if msg == DISCONNECT_MSG:
            connected = False
            for client in clients:
                if client['address'] != addr:
                    client['c'].send(f"\n[DISCONNECTED]...{addr[0]} {addr[1]} from the server".encode(FORMAT))
            for client in clients:
                if client["address"] == addr:
                    clients.remove(client)
                    break
            else:
                print(f'[ERROR] Cannot Disconnect {addr}')
        else:
            to_addr = (msg.split(':')[0], int(msg.split(':')[1]))
            msg = (msg.split(':')[2])
            msg = f"{to_addr} : {msg}"
            for client in clients:
                if client['address'] == to_addr:
                    try:
                        client["c"].send(msg.encode(FORMAT))
                        conn.send("Message sent".encode(FORMAT))
                    except BrokenPipeError:
                        print(f"[ERROR] cannot send message to {to_addr}")
                    break
    conn.close()
    
    
    
    
def main():
    print(f'[SERVER] Starting... ')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f'[SERVER] Listening on {IP}:{PORT}...')

    while True:
        conn, addr = server.accept()
        clients.append({"address": addr, "c": conn})
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')


if __name__ == "__main__":
    main()