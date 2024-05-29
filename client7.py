import socket
import threading
import sys
import sounddevice as sd
import os
import pickle

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024



def server_handle(client):
    duration = 20.5  # seconds

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        try:
            outdata[:] = indata
            client.send(pickle.dumps(indata))
        except socket.error as e:
            print("Socket error:", e)
        
        try:
            server_data=client.recv(1024)
            outdata[:] = pickle.loads(server_data)
        except socket.error as e:
            print("Socket error:", e)
            
    with sd.RawStream(channels=2, dtype='int24', callback=callback):
        sd.sleep(int(duration * 1000))




def main():
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f'[CONNECTED] Connected to server on {IP} : {PORT}')
    connected = True
    while connected:
   
        thread=threading.Thread(target=server_handle, args=(client,))
        thread.start()


if __name__ == '__main__':
    main()

