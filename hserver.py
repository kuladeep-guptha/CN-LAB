import socket
import cv2
import pickle
import struct
import threading
import datetime
import os

# Server IP and Ports
server_ip = '172.17.0.232'
video_port = 5566
chat_port = 1078
file_transfer_port = 1079
file_dir = "server_files"  # Directory to store received files

# Video Streaming Service
def handle_video_stream(client_socket):
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        data = pickle.dumps(frame)
        message = struct.pack("Q", len(data)) + data
        client_socket.sendall(message)
        cv2.imshow('Video from Client',frame)

        key = cv2.waitKey(1) & 0xFF
        if key ==ord('q'):
            client_socket.close()

def video_streaming_server():
    video_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_serv.bind((server_ip, video_port))
    video_serv.listen(5)

    while True:
        client, addr = video_serv.accept()
        print("hi")
        video_thread = threading.Thread(target=handle_video_stream, args=(client,))
        video_thread.start()

# Chat Service
def handle_chat(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received chat message: {message}")
        except Exception as e:
            print(f"Error receiving chat message: {str(e)}")
            break

def chat_server():
    chat_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat_serv.bind((server_ip, chat_port))
    chat_serv.listen(5)

    while True:
        client, addr = chat_serv.accept()
        chat_thread = threading.Thread(target=handle_chat, args=(client,))
        chat_thread.start()

# File Transfer Service
def handle_file_transfer(client_socket):
    try:
        file_info = client_socket.recv(1024).decode('utf-8')
        file_name, file_size = file_info.split(":")
        file_size = int(file_size)

        file_path = os.path.join(file_dir, file_name)

        with open(file_path, 'wb') as file:
            while file_size > 0:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                file_size -= len(data)

        print(f"Received file: {file_name}")
    except Exception as e:
        print(f"Error receiving file: {str(e)}")

def file_transfer_server():
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    file_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    file_serv.bind((server_ip, file_transfer_port))
    file_serv.listen(5)

    while True:
        client, addr = file_serv.accept()
        file_thread = threading.Thread(target=handle_file_transfer, args=(client,))
        file_thread.start()

# Licensing Service
valid_licenses = {
    "LICENSE-2024-10-25": datetime.datetime(2024, 10, 25),
    "LICENSE-2025-01-01": datetime.datetime(2025, 1, 1)
}

def verify_license(license_key):
    if license_key in valid_licenses:
        expiration_date = valid_licenses[license_key]
        if expiration_date > datetime.datetime.now():
            return True
    return False

# Start video streaming, chat, file transfer, and licensing services
video_streaming_server_thread = threading.Thread(target=video_streaming_server)
chat_server_thread = threading.Thread(target=chat_server)
file_transfer_server_thread = threading.Thread(target=file_transfer_server)
video_streaming_server_thread.start()
chat_server_thread.start()
file_transfer_server_thread.start()