import socket
import threading
import readline
import time


IP = socket.gethostbyname(socket.gethostname())
PORT= 5578
ADDR=(IP, PORT)
DISCONNECT_MSG = "DISCONNECT!"


clients = []
cinput=""

def printf(msg):
    input=readline.get_line_buffer()
    print(f"\r{msg}\n{cinput}{input}", end="", flush=True)
    
def inputtake(msg):
    global cinput
    cinput=msg
    out=input(f"\r{msg}")
    return out

def send_file(addr, msg):
    print("ji",msg)	
    for client in clients:
        if client["addr"]==addr:
            client["conn"].send(msg.encode())
            break
            


def handle_client(conn, addr):
    printf(f'[NEW CONNECTION] {addr} connected.')
    for client in clients:
        if client["addr"]!=addr:
            conn.send(f"l:({client['addr'][0]} {client['addr'][1]}) connected to server.".encode())
    for client in clients:
        if client["addr"]!=addr:
            client["conn"].send(f"l:({addr[0]} {addr[1]}) connected to server.".encode())
    
    connected = True
    while connected:
        ip=conn.recv(1024).decode()
        if not ip:
            continue
        if ip == DISCONNECT_MSG:
            connected = False
            for client in clients:
                if client["addr"]!=addr:
                    client["conn"].send(f"l:({addr[0]} {addr[1]}) disconnected from server.".encode())
            for client in clients:
                if client["addr"]==addr:
                    clients.remove(client)
                    break
            else:
                printf(f"cant disconnect {addr}")
            printf(f"\r{addr}{ip} disconnected")
            printf(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
            break
    
        address=(ip.split(' ')[0], int(ip.split(' ')[1]))
        for client in clients:
            if client["addr"]==address:
                break
        else:
            conn.send(f"e: {address}Client not found".encode())
            continue
        
        
        filename=conn.recv(1024).decode()
        send_file(address, filename)
        
        for client in clients:
            if client["addr"] == address:
                con1 = client["conn"]
        
        data=conn.recv(1024)
        while data!=b"EOF":
            con1.send(data)
            print("j")
            data=conn.recv(1024)
        time.sleep(0.1)
        con1.send(b"EOF")
        conn.send("a:File sent".encode())
        msg1=con1.recv(1024).decode()
        conn.send(f"{msg1} by {address}".encode())
    conn.close()
    
def main():
    printf('[SERVER] Starting... ')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    printf(f'[LISTENING] Server is listening on {IP}:{PORT}')
    while True:
        conn, addr = server.accept()
        clients.append({"conn": conn, "addr": addr})
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()       
        printf(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')

if __name__ == '__main__':
    main()
