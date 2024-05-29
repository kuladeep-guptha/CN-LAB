import socket
import threading
import time
import os
import pickle
import struct
from dataclasses import dataclass
from communication import *


IP=socket.gethostbyname(socket.gethostname())
port=6001
video_port=6002
audio_port=6003

clients={}
@dataclass
class Client_Details:
    name: str
    main_conn: socket.socket
    addr: str
    connected: bool
    video_conn: socket.socket = None
    audio_conn: socket.socket = None
    


def disconnect_client(client:Client_Details):
    global clients
    
    msg=Message(client.name,'remove_client')
    for client1 in clients:
        if client1!=client.name:
            conn=clients[client1].main_conn
            # msg=pickle.dumps(msg)
            # msg=struct.pack("i",len(msg))+msg
            # conn.sendall(msg)
            conn.send_bytes(pickle.dumps(msg))
    
    msg2=Message('server','disconnect')
    # msg2=pickle.dumps(msg2)
    # msg2=struct.pack("i",len(msg2))+msg2
    # client.main_conn.sendall(msg2)
    client.main_conn.send_bytes(pickle.dumps(msg2))
    client.main_conn.close()
    
    if client.video_conn:
        # client.video_conn.sendall(msg2)
        client.video_conn.send_bytes(pickle.dumps(msg2))
        client.video_conn.close()
    if client.audio_conn:
        # client.audio_conn.sendall(msg2)
        client.audio_conn.send_bytes(pickle.dumps(msg2))
        client.audio_conn.close()
    
    clients.pop(client.name)
    print(f"{client.name} disconnected")
    


def media_handler(name:str,media:str):
    client1=clients[name]
    if media=="video":
        conn=client1.video_conn
    elif media=="audio":
        conn=client1.audio_conn
    while client1.connected:
        msg=conn.recv_bytes()
        # print("hi")
        if not msg:
            break
        msg=pickle.loads(msg)
        msg=Message(name,msg.request,media,msg.data)
        for client in clients:
            if client!=name:
                if media=="video":
                    conn=clients[client].video_conn
                elif media=="audio":
                    conn=clients[client].audio_conn
                else:
                    print("error")
                    continue
                # msg=pickle.dumps(msg)
                # msg=struct.pack("i",len(msg))+msg
                # conn.sendall(msg)
                if conn:
                    conn.send_bytes(pickle.dumps(msg))
                    
    msg2=Message('server','disconnect')
    # msg2=pickle.dumps(msg2)
    # msg2=struct.pack("i",len(msg2))+msg2
    # conn.sendall(msg2)
    conn.send_bytes(pickle.dumps(msg2))
    conn.close()
    
    if media=="video":
        client1.video_conn=None       
    elif media=="audio":
        client1.audio_conn=None
    
    
def handle_client(name:str):
    client=clients[name]
    conn=client.main_conn
    
    for client1 in clients:
        msg=Message(client1,'add_client')
        if client1!=name:
            # msg=pickle.dumps(msg)
            # msg=struct.pack("i",len(msg))+msg
            # conn.sendall(msg)
            conn.send_bytes(pickle.dumps(msg))
    
    msg=Message(name,'add_client')
    for client1 in clients:
        if client1!=name:
            conn1=clients[client1].main_conn
            # msg=pickle.dumps(msg)
            # msg=struct.pack("i",len(msg))+msg
            # conn1.sendall(msg)
            conn1.send_bytes(pickle.dumps(msg))
    
    while client.connected:
        msg1=conn.recv_bytes()
        if not msg1:
            break
        msg1=pickle.loads(msg1)
        if msg1.request=="disconnect":
            client.connected=False
            break
        for name in msg1.to_names:
            if name not in clients:
                continue
            # msg1=pickle.dumps(msg1)
            # msg1=struct.pack("i",len(msg1))+msg1
            # clients[name].main_conn.sendall(msg1)
            clients[name].main_conn.send_bytes(pickle.dumps(msg1))
    disconnect_client(client)
    
        
          
        
        
        


def media_stream(media):
    if media=="video":
        port=video_port
    else:
        port=audio_port
    socket2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket2.bind((IP,port))
    socket2.listen()
    print(f"{media} server started at {IP}:{port}")
    while True:
        conn,addr=socket2.accept()
        name=conn.recv_bytes().decode()
        if media=="video":
            clients[name].video_conn=conn
        elif media=="audio":
            clients[name].audio_conn=conn
        print(f"{name} connected to {media} server")
        
        media_thread=threading.Thread(target=media_handler,args=(name,media))
        media_thread.start()
        
    #     if clients[addr[0]].video_conn and clients[addr[0]].audio_conn:
    #         clients[addr[0]].connected=True
    #         print(f"{addr[0]} connected to both servers")
    #     else:
    #         clients[addr[0]].connected=False
    #     while clients[addr[0]].connected:
    #         if media=="video":
    #             frame=clients[addr[0]].video_conn.recv_bytes()
    #             if frame:
    #                 clients[addr[0]].video_frame=frame
    #         else:
    #             audio=clients[addr[0]].audio_conn.recv_bytes()
    #             if audio:
    #                 clients[addr[0]].audio_frame=audio
    # socket2.close()


def main():
    socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket1.bind((IP,port))
    socket1.listen()
    print(f"server started at {IP}:{port}")
    
    video=threading.Thread(target=media_stream,args=("video",))
    video.start()
    audio=threading.Thread(target=media_stream,args=("audio",))
    audio.start()
    
    while True:
        conn,addr=socket1.accept()
        names=list(clients.keys())
        # msg=struct.pack("i",len(names))+pickle.dumps(names)
        # conn.sendall(msg)
        conn.send_bytes(pickle.dumps(names))
        
        name=conn.recv_bytes().decode()
        clients[name]=Client_Details(name,conn,addr,True)
        print(f"{name} connected")
        
            
        client_thread=threading.Thread(target=handle_client,args=(name,))
        client_thread.start()
    
    
if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"[EXITING] Keyboard Interrupt")
        for client in clients.values():
            disconnect_client(client)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        os._exit(0)
    

