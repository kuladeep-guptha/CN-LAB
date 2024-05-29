# import socket
# import threading
# import sys
# import sounddevice as sd
# import pickle

# IP=socket.gethostbyname(socket.gethostname())
# PORT=5566
# ADDR=(IP, PORT)
# DISCONNECT_MSG="DISCONNECT!"


# def handle_client(conn,addr):
#     duration = 20.5  # seconds
#     print("hi")
#     def callback(indata, outdata, frames, time, status):
#         if status:
#             print(status)
#         try:
#             print("hi1")
#             outdata[:] = indata
#             conn.send("hi".encode("utf-8"))
#         except socket.error as e:
#             print("Socket error:", e)
        
#         # try:
#         #     client_data=conn.recv(1024)
#         #     print("hi2")
#         #     outdata[:] = client_data
#         # except socket.error as e:
#         #     print("Socket error:", e)
            
#     with sd.RawStream(channels=2, dtype='int24', callback=callback):
#         sd.sleep(int(duration * 1000))
    



# def main():
#     print(f'[SERVER] Starting... ')
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind(ADDR)
#     server.listen()
#     print(f'[SERVER] Listening on {IP}:{PORT}')
#     while True:
#         conn, addr = server.accept()
#         thread = threading.Thread(target = handle_client, args = (conn,addr))
#         thread.start()
#         print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
        

# if  __name__ == '__main__':
#     main()
    
    
    
    
# # import sounddevice as sd
# # duration = 10.5  # seconds

# # def callback(indata, outdata, frames, time, status):
# #     if status:
# #         print(status)
# #     outdata[:] = indata

# # with sd.RawStream(channels=2, dtype='int24', callback=callback):
# #     sd.sleep(int(duration * 1000))

import socket
import pyaudio

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific IP and port
server_ip = "172.17.0.232"
server_port = 5566
s.bind((server_ip, server_port))

# Listen for incoming connections
s.listen(5)
print(f"Server listening on {server_ip}:{server_port}")

# Accept a connection from a client
client_socket, client_address = s.accept()
print(f"Connection from {client_address}")

# Set up audio playback
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)

# Start receiving and playing audio
while True:
    audio_data = client_socket.recv(1024)  # Receive audio data
    if not audio_data:
        break
    stream.write(audio_data)  # Play received audio data

# Close the client socket and audio stream when done
client_socket.close()
stream.stop_stream()
stream.close()
audio.terminate()
