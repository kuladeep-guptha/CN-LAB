
import cv2
import struct
import pyaudio
from PyQt6.QtCore import Qt, QThread, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QDockWidget \
    , QLabel, QWidget, QListWidget, QListWidgetItem \
    , QComboBox, QTextEdit, QLineEdit, QPushButton, QFileDialog,QMessageBox,QApplication,QDialog,QVBoxLayout,QTabWidget,QCheckBox 

import time
from communication import *
import socket

FRAME_WIDTH = 1080
FRAME_HEIGHT = 810
pa = pyaudio.PyAudio()

ENABLE_AUDIO = True
ENABLE_VIDEO = True

NO_CAM=cv2.imread("images/cam.jpeg.jpg")
cam_h, cam_w = NO_CAM.shape[:2]
cam_w, cam_h = (cam_w - FRAME_WIDTH//3)//2, (cam_h - FRAME_HEIGHT//3)//2
NO_CAM = NO_CAM[cam_h:cam_h+FRAME_HEIGHT//3, cam_w:cam_w+FRAME_WIDTH//3]
NO_MIC = cv2.flip(cv2.imread('images/mic.jpeg.jpg'), 1)

# class Client:
# active_clients = set()
# SEND_MSG = False
# CURRENT_MSG = None

# class Message:
#     def __init__(self, from_name: str, request: str, data_type: str = None, data: any = None, to_names: set[str] = set()):
#         self.from_name = from_name
#         self.request = request
#         self.data_type = data_type
#         self.data = data
#         self.to_names = to_names
#         self.file_name = None




# def recv_bytes(self):
#     raw_msglen = self.recvall(4)
#     if not raw_msglen:
#         return b''
#     msglen = struct.unpack("i", raw_msglen)[0]
#     return self.recvall(msglen)

# def recvall(self, n):
#     data = bytearray()
#     while len(data) < n:
#         packet = self.recv(n - len(data))
#         if not packet:
#             return b''
#         data.extend(packet)
#     return data


# socket.socket.recv_bytes = recv_bytes
# socket.socket.recvall = recvall

# def set_current_msg(msg: Message, send: bool = False):
#     global CURRENT_MSG, SEND_MSG
#     CURRENT_MSG = msg
#     SEND_MSG = True

# def get_send_msg():
#     global SEND_MSG
#     curr = SEND_MSG
#     SEND_MSG = False
#     return curr

# def get_current_msg():
#     global CURRENT_MSG
#     return CURRENT_MSG

# def get_active_clients():
#     return active_clients


class login_window(QDialog):
    def __init__(self):
        super().__init__()
        self.name = None
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        # self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)

        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def check_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        email1=email.split("@")
        self.name=email1[0]

        # Add your authentication logic here
        if email1[1] == "iiitdm.ac.in" and password == "password":
            print("hi4")
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid email or password")

    


class Audio:
    def __init__(self):
        self.audio_stream = pa.open(rate=48000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=2048)

    def get_stream(self):
       if not ENABLE_AUDIO:
            return None
       self.audio = self.audio_stream.read(2048, exception_on_overflow=False)
       return self.audio


class PlayAudio(QThread):
    def __init__(self, client):
        super().__init__()
        self.connected = True
        self.client = client
        self.audio_stream = pa.open(rate=48000, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=2048)

    def run(self):
        if self.client.audio is not None:
            return
        while self.connected:
            audio = self.client.get_audio()
            if audio is not None:
                self.audio_stream.write(audio)  
    




class Video:
    def __init__(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH//3)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT//3)

    def get_frame(self):
        global ENABLE_VIDEO, ENABLE_AUDIO
        if not ENABLE_VIDEO:
            frame = cv2.resize(NO_CAM, (FRAME_WIDTH//3, FRAME_HEIGHT//3), interpolation=cv2.INTER_AREA)
        else:
            success, frame = self.cap.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # convert frame to RGB
                frame = cv2.resize(frame, (FRAME_WIDTH//3, FRAME_HEIGHT//3), interpolation=cv2.INTER_AREA)
                frame = cv2.flip(frame, 1)
            else:
                return None
        if not ENABLE_AUDIO:
                nomic_h, nomic_w, _ = NO_MIC.shape
                x, y = FRAME_WIDTH//3 -  2 * nomic_w, FRAME_HEIGHT//3 - 2 * nomic_h
                frame[y:y+nomic_h, x:x+nomic_w] = NO_MIC.copy()
        return frame
        



class SelectClients(QWidget):
    def __init__(self, active_clients, msg_type, msg_data):
        super().__init__()
        self.active_clients = active_clients
        self.clients_checkbox = {}
        self.checked_clients = set()
        self.msg_type = msg_type
        self.msg_data = msg_data
        self.init_ui()

    # def init_ui(self):
    #     self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    #     self.setWindowTitle(f"Select Clients to Send {self.msg_type}")

    #     self.layout = QVBoxLayout()
    #     self.setLayout(self.layout)

    #     self.clients_list = QListWidget()
    #     self.clients_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
    #     self.clients_list.addItems(list(self.active_clients))

    #     self.select_all_button = QPushButton("Select All")
    #     self.select_all_button.clicked.connect(self.select_all)

    #     self.send_button = QPushButton(f"Send {self.msg_type}")
    #     self.send_button.clicked.connect(self.send_msg)

    #     self.layout.addWidget(self.clients_list)
    #     self.layout.addWidget(self.select_all_button)
    #     self.layout.addWidget(self.send_button)

    # def select_all(self):
    #     for i in range(self.clients_list.count()):
    #         self.clients_list.item(i).setSelected(True)

    # def send_msg(self):
    #     selected_clients = self.clients_list.selectedItems()
    #     selected_clients = [item.text() for item in selected_clients]
    #     msg = Message(None, 'post', self.msg_type, self.msg_data, selected_clients)
    #     set_current_msg(msg, True)
    #     self.close()
    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.setWindowTitle("Select Peers")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.h_layout = QHBoxLayout()
        self.layout.addLayout(self.h_layout)
        
        self.select_text = QLabel("Select Peers")
        self.select_all = QCheckBox("Select All")
        self.select_all.stateChanged.connect(self.select_all_clicked)

        self.h_layout.addWidget(self.select_text)
        self.h_layout.addWidget(self.select_all)

        for client in self.client_list:
            self.clients_checkbox[client] = QCheckBox(client)
            self.layout.addWidget(self.clients_checkbox[client])
        
        self.send_button = QPushButton("Send")
        self.layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_to_clients)
        
    def select_all_clicked(self):                    # to select all clients
        if self.select_all.isChecked():
            for client in self.client_list:
                self.clients_checkbox[client].setChecked(True)
        else:
            for client in self.client_list:
                self.clients_checkbox[client].setChecked(False)
    
    def send_to_clients(self):                      # to send message/file to selected clients
        atleast_one_checked = False
        for client in self.client_list:
            if self.clients_checkbox[client].isChecked():
                atleast_one_checked = True
                self.checked_clients.add(client)
        if atleast_one_checked:
            self.send_msg()
            self.close()
    
    def send_msg(self):
        print("sending message")
        msg = Message(None, 'post', self.msg_type, self.msg_data, self.checked_clients)
        set_current_msg(msg, True)










class SendPopup(QWidget):
    def __init__(self, **kwargs):         #
        super().__init__()
        self.init_ui(**kwargs)
    
    def init_ui(self, **kwargs):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.msg_type = kwargs.get('type', 'message')
        self.msg_path = kwargs.get('path', '')

        self.setWindowTitle(f"{self.msg_type} Sharing")

        self.button_text = self.msg_type + ' ' + self.msg_path
        self.label = QLabel(f"Enter {self.button_text}:")
        self.textbox = QLineEdit()

        if kwargs.get('file', False):                              
            self.textbox.setReadOnly(True)
            self.select_file_button = QPushButton("Select File")
            self.layout.addWidget(self.select_file_button)
            self.select_file_button.clicked.connect(self.select_file)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.label)
        horizontal_layout.addWidget(self.textbox)

        self.send_button = QPushButton(f"Send {self.msg_type}")

        self.layout.addLayout(horizontal_layout)
        self.layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.open_clients_list)

    def select_file(self):
        self.file_path = QFileDialog.getOpenFileName(self, 'Select File')[0]
        self.textbox.setText(self.file_path)
    
    def open_clients_list(self):
        msg = self.textbox.text()
        if msg != '' and not msg.isspace():
            self.close()
            self.clients_list_widget = SelectClients(get_active_clients(), msg_type=self.msg_type, msg_data=msg)
            self.clients_list_widget.show()


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.layout=QVBoxLayout()
        self.setLayout(self.layout)
        
        self.chat=QTextEdit()
        self.chat.setReadOnly(True)
        self.layout.addWidget(self.chat)
        
        self.input=QLineEdit()
        self.layout.addWidget(self.input)
        
        self.send=QPushButton("send message")
        self.layout.addWidget(self.send)
        self.send.clicked.connect(self.send_msg)
        
        self.file=QPushButton("send file")
        self.layout.addWidget(self.file)
        self.file.clicked.connect(self.send_file)
        
        
        
    def send_msg(self):
        self.popup=SendPopup(type='message',file=False)
        self.popup.show()
    def send_file(self):
        self.popup=SendPopup(type='file',path='path',file=True)
        self.popup.show()


class VideoWidget(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()
        self.timer=QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.name_label = QLabel(self.client.name)          # to display client name
        self.video_frame = QLabel()                         # to display client video

        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.video_frame)
        
        
        
    def update_frame(self):
        frame=self.client.get_video()
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_frame.setPixmap(QPixmap.fromImage(image))
            
        
    
class videolistwidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.all_items={}
        self.init_ui()
        
    def init_ui(self):
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
    
    def add_video(self, client, frame=None):
        video_widget = VideoWidget(client)
        print("hi2")
        item = QListWidgetItem()
        item.setFlags(item.flags() & ~(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled))
        self.addItem(item)
        item.setSizeHint(QSize(FRAME_WIDTH//3, FRAME_HEIGHT//3))
        self.setItemWidget(item, video_widget)
        self.all_items[client.name] = item
    
    def remove_video(self, name):
        self.removeItemWidget(self.all_items[name])
        self.all_items.pop(name)
        

        

class MainWindow(QMainWindow):
    def __init__(self,client,server):
        super().__init__()
        self.client = client
        self.server = server
        self.audio_threads = {}
        self.server.add_client_signal.connect(self.add_client)
        self.server.remove_client_signal.connect(self.remove_client)
        self.server.add_msg_signal.connect(self.add_msg)
        self.server.start()

        self.init_ui()
        

    def init_ui(self):
        self.setWindowTitle("Video Conferencing")
        self.setGeometry(0, 0, 1920, 1000)
        login=login_window()
        if not login.exec():
            self.close()
            exit(0)
        else:
            self.client.name=login.name      
        self.tab=QTabWidget()
        self.video_list_widget = videolistwidget()
        self.chat=ChatWidget()
        self.add_toggle_buttons()
        # self.setCentralWidget(self.video_list_widget)
        
        # self.sidebar=QDockWidget("sidebar",self)
       
        # self.sidebar.setWidget(self.chat)
        # self.sidebar.setFixedWidth(250)
        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.sidebar)
        # self.sidebar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        #seperate tab
        
        self.tab.addTab(self.video_list_widget,"Video")
        self.tab.addTab(self.chat,"Chat")
        self.setCentralWidget(self.tab)
        # self.layout=QVBoxLayout()
        # self.layout.addWidget(self.tab)
        # self.setLayout(self.layout)
    
    def add_toggle_buttons(self):
        self.enable_video = QCheckBox("Video")
        self.enable_video.setChecked(True)
        self.enable_video.stateChanged.connect(lambda: self.toggle_media('video'))

        self.enable_audio = QCheckBox("Audio")
        self.enable_audio.setChecked(True)
        self.enable_audio.stateChanged.connect(lambda: self.toggle_media('audio'))

        self.end_call = QPushButton("Leave Call")
        # change its color to red and round edges
        self.end_call.setStyleSheet("background-color: #F15A59;")
        self.end_call.clicked.connect(self.close)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.enable_video)
        h_layout.addWidget(self.enable_audio)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.end_call)

        self.chat.layout.addLayout(v_layout)
    
    def toggle_media(self, media):
        global ENABLE_VIDEO, ENABLE_AUDIO
        if media == 'video':
            if self.enable_video.isChecked():
                ENABLE_VIDEO = True
            else:
                ENABLE_VIDEO = False
        elif media == 'audio':
            if self.enable_audio.isChecked():
                ENABLE_AUDIO = True
            else:
                ENABLE_AUDIO = False
        
    def add_client(self, client):
        self.video_list_widget.add_video(client)
        self.audio_threads[client.name] = PlayAudio(client)
        self.audio_threads[client.name].start()
        msg=Message(client.name,'join','message','joined the meeting',None)
        self.add_msg(msg)
        
    def remove_client(self, name):
        self.video_list_widget.remove_video(name)
        self.audio_threads[name].connected = False
        self.audio_threads[name].wait()
        self.audio_threads.pop(name)
        self.chat_widget.chat_box.append(f"{name} left the conference")
        
    def add_msg(self,msg):
        if self.client.name!=msg.from_name:
            if msg.data_type=='message':
                chat=f"{msg.from_name}: {msg.data}"
            elif msg.data_type=='file' and msg.file_name is not None:
                chat=f"{msg.from_name}: {msg.data}"
                
        else:
            if msg.data_type=='message':
                chat=f"kula:{msg.data}"
            elif msg.data_type=='file' and msg.file_name is not None:
                chat=f"kula:{msg.data}"
            if msg.request!='join':
                chat=chat+'\n sent to['
                for name in msg.to_names:
                    chat=chat+name+','
                chat=chat[:-2]+']'
                
        self.chat.chat.append(chat)
        


        
        


        

        
        
    
        

        
    








    

