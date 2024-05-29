import socket
import cv2
import pickle
import struct
import threading
import os
import datetime

# Server IP and Ports
server_ip = '192.168.137.225'
video_port = 1077
chat_port = 1078
file_transfer_port = 1079

# Licensing Check
def check_license(license_key):
    # Define a dictionary of valid license keys and their expiration dates
    valid_licenses = {
        "LICENSE-2024-10-25": datetime.datetime(2024, 10, 25),
        "LICENSE-2025-01-01": datetime.datetime(2025, 1, 1)
    }

    # Check if the provided license key is in the valid licenses dictionary
    if license_key in valid_licenses:
        # Get the expiration date associated with the license key
        expiration_date = valid_licenses[license_key]

        # Check if the current date is before the expiration date
        current_date = datetime.datetime.now()
        if current_date < expiration_date:
            return True  # License is valid and not expired
        else:
            print("License has expired.")
    else:
        print("Invalid license key.")

    return False  # License is not valid

# Video Streaming Client
def receive_video_stream():
    video_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_client.connect((server_ip, video_port))
    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        while len(data) < payload_size:
            packet = video_client.recv(4096)
            if not packet:
                break
            data += packet

        packed_msg = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg)[0]

        while len(data) < msg_size:
            data += video_client.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("Video from Server", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video_client.close()
    cv2.destroyAllWindows()

# Chat Client
chat_active = False
a = 0

def send_chat_message():
    global chat_active
    chat_active = True
    chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat_client.connect((server_ip, chat_port))

    while chat_active:
        message = input("Chat: ")
        chat_client.send(message.encode('utf-8'))
        if message.lower() == "exit":
            a = 1
            chat_active = False
        
def receive_chat_messages():
    chat_active = True
    chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat_client.connect((server_ip, chat_port))

    while chat_active:
        try:
            if a == 1:
                break
            message = chat_client.recv(1024).decode('utf-8')
            if not message:
                chat_active = False
                break
            print(f"Received: {message}")
        except Exception as e:
            print(f"Error receiving chat message: {str(e)}")
            chat_active = False
            break

# File Transfer Client
def send_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        file_info = f"{file_name}:{file_size}"
        file_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_client.connect((server_ip, file_transfer_port))
        file_client.send(file_info.encode('utf-8'))

        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                file_client.send(data)
                data = file.read(1024)

        file_client.close()
        print(f"File sent: {file_name}")
    except Exception as e:
        print(f"Error sending file: {str(e)}")

# File Sending Thread
def send_file_thread():
    file_path = input("Enter the path to the file you want to send: ")
    if os.path.exists(file_path):
        send_file(file_path)
        print("File sent successfully.")
    else:
        print("File not found.")

def main_menu():
    while True:
        print("\nMenu:")
        print("1. Start Video Streaming")
        print("2. Chat")
        print("3. Send File")
        print("4. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            video_thread = threading.Thread(target=receive_video_stream)
            video_thread.start()
        elif choice == "2":
            chat_send_thread = threading.Thread(target=send_chat_message)
            #chat_receive_thread = threading.Thread(target=receive_chat_messages)
            chat_send_thread.start()
            #chat_receive_thread.start()
            chat_send_thread.join()
            #chat_receive_thread.join()
        elif choice == "3":
            file_thread = threading.Thread(target=send_file_thread)
            file_thread.start()
            file_thread.join()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a valid option.")


# Client-Side Licensing Check
license_key = "LICENSE-2025-01-01"
if check_license(license_key):
    main_menu()
else:
    print("Invalid or expired license. Video streaming, chat, and file transfer services are disabled.")