import socket
import pickle
import sys, time, os
from PyQt6.QtCore import QThreadPool, QThread, pyqtSignal, QRunnable, pyqtSlot
from PyQt6.QtWidgets import QApplication
from gui import MainWindow, Video, Audio
from middle_man import *

# Server IP and port
IP = socket.gethostbyname(socket.gethostname())
port = 6636
video_port = 6637
audio_port= 6638


# clients
class Client:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.video = None
        self.audio = None
        self.camera_enabled = True
        self.microphone_enabled = True

        self.video_frame = None
        self.audio_stream = None

        if self.addr is None:
            self.video = Video()
            self.audio = Audio()

    def get_video(self):
        if self.video is not None:
            return self.video.get_frame()

        return self.video_frame
    
    def get_audio(self):
        if self.audio is not None:
            return self.audio.get_stream()

        return self.audio_stream

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)

class ServerConnection(QThread):
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

    def run(self):                                                      ###who is calling this
        while client.name == 'You':
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

        print("Sending name: ", client.name)
        self.main_socket.send_bytes(client.name.encode())             ####
        time.sleep(1)
        self.video_socket.send_bytes(client.name.encode())
        self.audio_socket.send_bytes(client.name.encode())
    
    def start_conn_threads(self):
        self.threadpool.start(Worker(self.handle_main, self.main_socket))
        
        self.threadpool.start(Worker(self.handle_media, self.video_socket, 'video'))
        self.threadpool.start(Worker(self.handle_media, self.audio_socket, 'audio'))

    def start_broadcast_threads(self):
        self.threadpool.start(Worker(self.multicast_msg, self.main_socket, 'msg'))
        self.threadpool.start(Worker(self.broadcast_media, self.video_socket, 'video'))
        self.threadpool.start(Worker(self.broadcast_media, self.audio_socket, 'audio'))
    
    def disconnect(self):
        msg = Message(client.name, 'disconnect')
        self.main_socket.send_bytes(pickle.dumps(msg))
        self.main_socket.disconnect()        #########
        self.video_socket.disconnect()
        self.audio_socket.disconnect()
        
    def handle_main(self, conn):                 
        global all_clients, active_clients               ##receiving messaf=ges from another client
        while self.connected:
            msg_bytes = conn.recv_bytes()           ##
            if not msg_bytes:
                self.connected = False
                break
            msg = pickle.loads(msg_bytes)
            if type(msg) != Message:
                print("Clients: ", msg)
            elif msg.request == 'disconnect':
                self.connected = False
                break
            elif msg.request == 'add_client':                    ##when a clients ask to add
                client_name = msg.from_name
                all_clients[client_name] = Client(client_name, "addr")      ##
                active_clients.add(client_name)
                self.add_client_signal.emit(all_clients[client_name])    ##emit arguments
                print("Added client: ", client_name)
            elif msg.request == 'remove_client':
                client_name = msg.from_name
                self.remove_client_signal.emit(client_name)
                all_clients.pop(client_name)
            elif msg.request == 'post':
                if msg.data_type == 'file':
                    file_name = msg.file_name
                    with open(file_name, 'wb') as file:
                        file.write(msg.data)
                self.add_msg_signal.emit(msg)
            else:
                print("Invalid request: ", msg.request)

    def handle_media(self, conn, media):
        global all_clients
        while self.connected:
            msg_bytes = conn.recv_bytes()
            if not msg_bytes:
                self.connected = False
                break
            msg = pickle.loads(msg_bytes)
            if msg.request == 'disconnect':                  ###?          receiving video and audio frames from another client
                self.connected = False
                break
            if msg.request == 'post':
                client_name = msg.from_name
                if client_name not in all_clients:
                    continue
                if msg.data_type == 'video':
                    all_clients[client_name].video_frame = msg.data
                elif msg.data_type == 'audio':
                    all_clients[client_name].audio_stream = msg.data
    
    def multicast_msg(self, conn, msg):
        global SEND_MSG
        while self.connected:
            proceed = get_send_msg()
            if not proceed:
                continue
            print("Sending message...")                                                ##Sending files from client to server
            current_msg = get_current_msg()
            current_msg.from_name = client.name
            if current_msg.data_type == 'file':
                file_path = current_msg.data
                current_msg.file_name = current_msg.data.split('/')[-1]
                with open(file_path, 'rb') as file:
                    current_msg.data = file.read()
            msg = pickle.dumps(current_msg)
            self.add_msg_signal.emit(current_msg)
            conn.send_bytes(msg)
    
    def broadcast_media(self, conn, media):
        while self.connected:
            if media == 'video':
                data = client.get_video()                      
            elif media == 'audio':                                                      ##sending audio and video frames
                data = client.get_audio()
            else:
                print("Invalid media type")
                break
            msg = Message(client.name, 'post', media, data)
            conn.send_bytes(pickle.dumps(msg))

client = Client('You', None)
all_clients = {}
def main():
    app = QApplication(sys.argv)

    server = ServerConnection()
    window = MainWindow(client, server)
    window.show()

    app.exec()
    server.disconnect()         ####
    os._exit(0)

    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n> Disconnecting...")
        exit(0)