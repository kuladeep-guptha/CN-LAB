import socket
import sounddevice as sd
import numpy as np

# Set up a socket to listen for incoming data
host = socket.gethostbyname(socket.gethostname())
port = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Waiting for a connection...")
conn, addr = server_socket.accept()
print(f"Connection from {addr}")

# Receive and deserialize audio data
received_data = conn.recv(1024)
audio_data = np.frombuffer(received_data, dtype='int16')

# Playback audio
sd.play(audio_data, samplerate=44100)
sd.wait()

conn.close()
