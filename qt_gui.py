import cv2
import pyaudio
from PyQt6.QtCore import Qt, QThread, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QDockWidget \
    , QLabel, QWidget, QListWidget, QListWidgetItem \
    , QComboBox, QTextEdit, QLineEdit, QPushButton, QFileDialog

import time

SAMPLE_RATE = 48000
BLOCK_SIZE = 128
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

pa = pyaudio.PyAudio()


class Microphone:
    def __init__(self):
        self.stream = pa.open(
            rate=SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=BLOCK_SIZE
        )

    def get_data(self):
        return self.stream.read(BLOCK_SIZE)


class AudioThread(QThread):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.stream = pa.open(
            rate=SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            output=True,
            frames_per_buffer=BLOCK_SIZE
        )

    def run(self):
        while True:
            self.update_audio()

    def update_audio(self):
        data = self.client.get_audio()
        if data is not None:
            self.stream.write(data)


class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame


class VideoWidget(QWidget):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video)

        self.init_video()

    def init_ui(self):
        # self.resize(FRAME_WIDTH, FRAME_HEIGHT)
        self.video_viewer = QLabel()
        self.name_label = QLabel(self.client.name)
        self.video_viewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_viewer)
        self.layout.addWidget(self.name_label)
        self.setLayout(self.layout)
    
    def init_video(self):
        self.timer.start(30)
    
    def update_video(self):
        frame = self.client.get_video()
        if frame is not None:
            # print(frame.shape)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_viewer.setPixmap(QPixmap.fromImage(q_img))


class VideoListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)

    def add_client(self, client):
        video_widget = VideoWidget(client)

        item = QListWidgetItem()
        item.setFlags(item.flags() & ~(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled))
        self.addItem(item)
        # item.setSizeHint(video_widget.sizeHint())
        item.setSizeHint(QSize(FRAME_WIDTH, FRAME_HEIGHT))
        self.setItemWidget(item, video_widget)


class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.clients_combo_box = QComboBox(self)
        self.clients_combo_box.addItems(["Client 1", "Client 2", "Client 3"])
        self.layout.addWidget(self.clients_combo_box)

        self.central_widget = QTextEdit(self)
        self.central_widget.setReadOnly(True)
        self.layout.addWidget(self.central_widget)

        self.bottom_layout = QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)

        self.line_edit = QLineEdit(self)
        self.bottom_layout.addWidget(self.line_edit)

        self.file_button = QPushButton("Select File", self)
        self.bottom_layout.addWidget(self.file_button)
        self.file_button.clicked.connect(self.select_file)

        self.send_button = QPushButton("Send", self)
        self.bottom_layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_text)
    
    def select_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select File")[0]
        self.send_file(file_path)

    def send_text(self):
        text = self.line_edit.text()
        client_name = self.clients_combo_box.currentText()
        self.central_widget.append(f"You -> {client_name}: {text}")
        self.line_edit.clear()
    
    def send_file(self, file_path):
        file_name = file_path.split("/")[-1]
        client_name = self.clients_combo_box.currentText()
        self.central_widget.append(f"You -> {client_name}: {file_path}")


class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.audio_threads = []

        self.init_ui()
        self.init_client(self.client)

    def init_ui(self):
        self.setWindowTitle("Video Conferencing")
        self.setGeometry(100, 100, 1080, 720)

        self.video_list_widget = VideoListWidget()
        self.setCentralWidget(self.video_list_widget)

        self.sidebar = QDockWidget("Chat", self)
        self.chat_widget = ChatWidget()
        self.sidebar.setWidget(self.chat_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidebar)
    
    def init_client(self, client):
        self.video_list_widget.add_client(client)

        self.audio_threads.append(AudioThread(client))
        self.audio_threads[-1].start()