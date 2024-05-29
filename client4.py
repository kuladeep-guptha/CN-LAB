import socket
import threading
import readline
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5578
ADDR = (IP, PORT)
DISCONNECT_MSG = "DISCONNECT!"

clients = []
cinput = ""


def printf(msg):
    input = readline.get_line_buffer()
    print(f"\r{msg}\n{cinput}{input} ", end="", flush=True)


def inputtake(msg):
    global cinput
    cinput = msg
    out = input(f"\r{msg}")
    return out


def handle_client(conn, addr):
    connected = True
    while connected:
        filename = conn.recv(1024).decode()
        if not filename:
            print("disconnected")
            break
        print(filename)
        type = filename.split(":")[0]
        file = filename.split(":")[1]
        print(file)
        if type == "a":
            printf(f"[receiving] receiving {file}")
            continue
        if type == "l":
            printf(f"[{addr}] {file}")
            continue

        with open(file, "wb") as f:
            printf(f"[receiving] receiving {file}")
            data = conn.recv(1024)
            while data != b"EOF":
                f.write(data)
                data = conn.recv(1024)
            printf(f"[received] received {file}")
            conn.send("a:[server] File received".encode())
            f.close()
    conn.close()


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    printf(f'[CONNECTED] Connected to server on {IP} : {PORT}')

    thread = threading.Thread(target=handle_client, args=(client, ADDR))
    thread.start()

    connected = True
    while connected:
        msg = inputtake("(IP PORT) > ")
        if msg == DISCONNECT_MSG:
            printf(f"[DISCONNECTED].. Disconnected from {IP} : {PORT}")
            client.send(msg.encode())
            break
        else:
            client.send(msg.encode())

        filename = inputtake("Enter the filename: ")
        client.send(f"f:{filename}".encode())

        with open(filename, "rb") as f:
            time.sleep(0.1)
            printf(f"[sending] sending {filename}")
            while True:
                data = f.read(1024)
                if not data:
                    break
                client.send(data)
                print("hu")
            time.sleep(0.1)
            client.send(b"EOF")
            printf(f"[sent] sent {filename}")
            f.close()
    client.close()


if __name__ == '__main__':
    main()
