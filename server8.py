import socket
import sounddevice as sd

# Set up a socket connection
server_ip = socket.gethostbyname(socket.gethostname())
port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, port))

# Capture audio
duration = 5.0
audio_data = sd.rec(int(duration * 44100), samplerate=44100, channels=2, dtype='int16')
sd.wait()

# Serialize and send audio data
client_socket.send(audio_data.tobytes())
client_socket.close()
