# import sounddevice as sd
# import socket
# import numpy as np

# # Server address and port
# server_ip = 'server_ip_here'
# server_port = 12345

# duration = 5.5  # seconds

# def client_callback(indata, outdata, frames, time, status):
#     if status:
#         print(status)

#     # Send the audio data to the server
#     try:
#         client_socket.sendall(np.array(indata).tobytes())
#     except socket.error as e:
#         print("Socket error:", e)

# # Create a RawStream for the client
# with sd.RawStream(channels=2, dtype='int24', callback=client_callback):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#         client_socket.connect((server_ip, server_port))
#         sd.sleep(int(duration * 1000))


import sounddevice as sd
duration = 10.5  # seconds

def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata

with sd.RawStream(channels=2, dtype='int24', callback=callback):
    sd.sleep(int(duration * 1000))











































































