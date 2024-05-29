import socket
import pickle
import sys
import struct
import time
from PyQt6.QtCore import QThreadPool, QThread, pyqtSignal, QRunnable, pyqtSlot
from PyQt6.QtWidgets import QApplication
from communication import *
from gui2 import MainWindow, Video, Audio


IP=socket.gethostbyname(socket.gethostname())
port=6001
video_port=6002
audio_port=6003



class Client:
    def __init__(self,name,addr):
        self.name=name
        self.addr=addr
        self.video=None
        self.audio=None
        self.videoframe=None
        self.audiostream=None
        
        if self.addr is None:
            self.video=Video()
            self.audio=Audio()
            
    def get_video(self):
        if self.video is not None:
            return self.video.get_frame()

        return self.videoframe     
    
    def get_audio(self):
        if self.audio is not None:
            return self.audio.get_stream()

        return self.audiostream
    
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)
        


class handling_server_conn(QThread):
    add_client_signal = pyqtSignal(Client)
    remove_client_signal = pyqtSignal(str)
    add_msg_signal = pyqtSignal(Message)
    
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False

    def run(self):
        while client.name == 'kula':
            pass

        self.init_connection()
        self.start_conn_threads()
        self.start_broadcast_threads()

        self.add_client_signal.emit(client)

        while self.connected:
            pass
        
    def init_connection(self):
        self.main_socket.connect((IP, port))
        self.video_socket.connect((IP, video_port))
        self.audio_socket.connect((IP, audio_port))
        self.connected = True
        
        print("sending name: ", client.name)
        # msg=client.name.encode()
        # msg=struct.pack("i",len(msg))+msg
        # self.main_socket.sendall(msg)
        self.main_socket.send_bytes(client.name.encode())
        time.sleep(1)
        # self.video_socket.sendall(msg)
        # self.audio_socket.sendall(msg)
        self.video_socket.send_bytes(client.name.encode())
        self.audio_socket.send_bytes(client.name.encode())
        
        
    def start_conn_threads(self):
        self.threadpool.start(Worker(self.main_conn_handler, self.main_socket))
        self.threadpool.start(Worker(self.media_handler, self.video_socket,'video'))
        self.threadpool.start(Worker(self.media_handler, self.audio_socket,'audio'))
        
        
    def start_broadcast_threads(self):
        self.threadpool.start(Worker(self.multicast_handler, self.main_socket,'msg'))
        self.threadpool.start(Worker(self.broadcast_handler, self.video_socket,'video'))
        self.threadpool.start(Worker(self.broadcast_handler, self.audio_socket,'audio'))
    

    def disconnect(self):
        msg=Message(client.name,'disconnect')
        self.main_socket.send_bytes(pickle.dumps(msg))
        msg1=Message('SERVER','disconnect')
        self.main_socket.send_bytes(pickle.dumps(msg1))
        self.main_socket.close()
        self.video_socket.send_bytes(pickle.dumps(msg1))
        self.video_socket.close()
        self.audio_socket.send_bytes(pickle.dumps(msg1))
        self.audio_socket.close()
        
        
    
    
    def main_conn_handler(self,conn):
        global clients,active_clients
        while self.connected:
            msg1=conn.recv_bytes()
            if not msg1:
                self.connected=False
                break
            msg2=pickle.loads(msg1)               #
            if type(msg2)!=Message:
                print("Clients:",msg1)
            elif msg1.request=="disconnect":
                self.connected=False
                break
            elif msg2.request=="add_client":
                print("hi3")
                clients[msg2.from_name]=Client(msg2.from_name,"addr")
                active_clients.add(msg2.from_name)
                self.add_client_signal.emit(clients[msg2.from_name])
                print("add_client",msg2.from_name)
            elif msg1.request=="remove_client":
                self.remove_client_signal.emit(msg2.from_name)
                active_clients.remove(msg2.from_name)
                print("remove_client",msg2.from_name)
                clients.pop(msg2.from_name)
            elif msg1.request=="post":
                if msg1.data_type=='file':
                    file_name=msg2.file_name
                    with open(file_name,'wb') as f:
                        f.write(msg2.data)
                self.add_msg_signal.emit(msg2)
            else:
                print("unknown request",msg2.request)
                
        
    def media_handler(self,conn,media):
        global clients
        while self.connected:
            msg1=conn.recv_bytes()
            if not msg1:
                self.connected=False
                break
            msg2=pickle.loads(msg1)
            if msg2.request=="disconnect":
                self.connected=False
                break
            if msg2.request=='post':
                name=msg2.from_name
                media=msg2.data_type
                if name not in clients:
                    continue
                if media=='video':
                    clients[name].videoframe=msg2.data
                elif media=='audio':
                    clients[name].audiostream=msg2.data

    def multicast_handler(self,conn,media):
        global SEND_MSG
        while self.connected:
            k=get_send_msg()
            if not k:
                continue
            print("sending message")
            msg1=get_current_msg()
            msg1.from_name=client.name
            if msg1.data_type=='file':
                file_path=msg1.data           ###
                msg1.file_name=msg1.data.split('/')[-1]
                with open(file_path,'rb') as f:
                    msg1.data=f.read()
            msg2=pickle.dumps(msg1)
            self.add_msg_signal.emit(msg1)
            
            # msg2=struct.pack("i",len(msg2))+msg2
            # conn.sendall(msg2)
            conn.send_bytes(msg2)
            

    def broadcast_handler(self,conn,media):
        while self.connected:
            if media=='video':
                frame=client.get_video()
            elif media=='audio':
                frame=client.get_audio()
            else:
                print("error")
                break
            msg=Message(client.name,'post',media,frame)
            msg=pickle.dumps(msg)
            # msg=struct.pack("i",len(msg))+msg
            # conn.sendall(msg)
            conn.send_bytes(msg)
        
        
client=Client("kula",None)
clients={}

def main():
    app = QApplication(sys.argv)
    server_conn = handling_server_conn()
    window = MainWindow(client,server_conn)
    window.show()
    app.exec()
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n> Disconnecting...")
        exit(0)
        