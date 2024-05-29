import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
import pyaudio
from array import array
from threading import Thread
import numpy as np
import zlib
import struct

HOST = '172.17.2.154'
PORT_VIDEO = 3000
PORT_AUDIO = 4000
PORT_CHAT = 5000

BufferSize = 4096
CHUNK = 1024
lnF = 640 * 480 * 3
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100


def Recieve():
    while True:
        try:
            msg = client.recv(BufferSize).decode("utf-8")
            print(msg)
        except OSError:
            break


def Send():
    while True:
        try:
            msg = input()
            if msg == "quit":
                client.send(msg.encode("utf-8"))
                client.close()
                break
            else:
                client.send(msg.encode("utf-8"))
        except Exception as e:
            print(f"Error in Send: {e}")


def SendAudio():
    while True:
        try:
            data = stream.read(CHUNK)
            dataChunk = array('h', data)
            vol = max(dataChunk)
            clientAudioSocket.sendall(data)
        except Exception as e:
            print(f"Error in SendAudio: {e}")


def RecieveAudio():
    while True:
        try:
            data = recvallAudio(BufferSize)
            stream.write(data)
        except Exception as e:
            print(f"Error in RecieveAudio: {e}")


def recvallAudio(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        databytes += clientAudioSocket.recv(to_read)
    return databytes


def SendFrame():
    while True:
        try:
            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            frame = np.array(frame, dtype=np.uint8).reshape(1, lnF)
            jpg_as_text = bytearray(frame)

            databytes = zlib.compress(jpg_as_text, 9)
            length = struct.pack('!I', len(databytes))
            bytesToBeSend = b''
            clientVideoSocket.sendall(length)
            while len(databytes) > 0:
                if (5000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(5000 * CHUNK)]
                    databytes = databytes[(5000 * CHUNK):]
                    clientVideoSocket.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    clientVideoSocket.sendall(bytesToBeSend)
                    databytes = b''
        except Exception as e:
            print(f"Error in SendFrame: {e}")


def RecieveFrame():
    while True:
        try:
            lengthbuf = recvallVideo(4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvallVideo(length)
            img = zlib.decompress(databytes)
            if len(databytes) == length:
                img = np.array(list(img))
                img = np.array(img, dtype=np.uint8).reshape(480, 640, 3)
                cv2.imshow("Stream", img)
                if cv2.waitKey(1) == 27:
                    cv2.destroyAllWindows()
            else:
                print("Data CORRUPTED")
        except Exception as e:
            print(f"Error in RecieveFrame: {e}")


def recvallVideo(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        databytes += clientVideoSocket.recv(to_read)
    return databytes


client = socket(family=AF_INET, type=SOCK_STREAM)

try:
    client.connect((HOST, PORT_CHAT))
except Exception as e:
    print(f"Error in connecting to chat server: {e}")
    exit()

RecieveThread = Thread(target=Recieve).start()
SendThread = Thread(target=Send).start()

clientVideoSocket = socket(family=AF_INET, type=SOCK_STREAM)

try:
    clientVideoSocket.connect((HOST, PORT_VIDEO))
except Exception as e:
    print(f"Error in connecting to video server: {e}")
    exit()

wvs = WebcamVideoStream(0).start()

clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)

try:
    clientAudioSocket.connect((HOST, PORT_AUDIO))
except Exception as e:
    print(f"Error in connecting to audio server: {e}")
    exit()

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

initiation = clientVideoSocket.recv(5).decode()

if initiation == "start":
    SendFrameThread = Thread(target=SendFrame).start()
    SendAudioThread = Thread(target=SendAudio).start()
    RecieveFrameThread = Thread(target=RecieveFrame).start()
    RecieveAudioThread = Thread(target=RecieveAudio).start()