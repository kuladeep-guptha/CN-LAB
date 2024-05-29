import socket
import pygame
import pickle
import os
import time
import re

import tkinter as tk
from tkinter import messagebox
from getmac import get_mac_address

IP = socket.gethostbyname(socket.gethostname())
PORT = 8081
ADDR = (IP, PORT)                                           
SIZE = 4096
DISCONNECT_MESSAGE = "DISCONNECT"
CONNECTED = False
IN_QUEUE = True

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

WIDTH, HEIGHT = 600, 400
PLAYER_SIZE = 30
COIN_SIZE = 15
BACKGROUND = (0, 0, 0)
COIN_COLOR = (137, 207, 240)
countdown = 10  # Initial countdown value

def game_entry():
    def register():
        mac_address_pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        match = re.match(mac_address_pattern, mac_entry.get())
        if not match:
            messagebox.showerror("Invalid MAC Address", "Invalid MAC Address")
        else:
            mac = mac_entry.get()
            client.send(pickle.dumps(f"REGISTER/{mac}"))
            msg = recv_msg(client)
            if msg == "OK":
                print(f"Registered MAC Address: {mac}")
                messagebox.showinfo("Registration Successful", f"Registered MAC Address: {mac}")
            else:
                print(f"Registration Failed: {msg}")
                messagebox.showerror("Registration Failed", f"Registration Failed: {msg}")
    
    def login():
        mac = mac_entry.get()
        client.send(pickle.dumps(f"LOGIN/{mac}"))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Logged in with MAC Address: {mac}")
            start_tk.destroy()
        else:
            print(f"Login Failed: {msg}")
            messagebox.showerror("Login Failed", f"Login Failed: {msg}")

    def pay():
        msg, t = "", 0
        try:
            if int(amount_entry.get()) <= 0:
                t = 1
                messagebox.showerror("Invalid Amount", "Amount should be greater than 0")
            else:
                float(amount_entry.get())
                mac = mac_entry.get()
                amount = amount_entry.get()
                client.send(pickle.dumps(f"PAY/{mac}/{amount}"))
                msg = recv_msg(client)
        except:
            t = 1
            messagebox.showerror("Invalid Amount", "Amount should be a number")
        if msg == "OK":
            print(f"Paid {amount} for MAC Address: {mac}")
            messagebox.showinfo("Payment Successful", f"Paid {amount} for MAC Address: {mac}")
        elif t == 0:
            print(f"Payment Failed: {msg}")
            messagebox.showerror("Payment Failed", f"Payment Failed: {msg}")
    
    def end_tk():
        start_tk.destroy()
        disconnect_server(client, "client")

    start_tk = tk.Tk()
    start_tk.title("Game Registration/Login")
    
    mac_label = tk.Label(start_tk, text="MAC Address:")
    mac_label.grid(row=0, column=0)
    mac_entry = tk.Entry(start_tk)
    mac_entry.grid(row=0, column=1)

    mac_entry.insert(0, get_mac_address())
    # mac_entry.config(state='readonly') # comment this line to run on local machine
    
    amount_label = tk.Label(start_tk, text="Amount (100/min):")
    amount_label.grid(row=2, column=0)
    amount_entry = tk.Entry(start_tk)
    amount_entry.grid(row=2, column=1)

    amount_entry.insert(0, "100")
    
    register_button = tk.Button(start_tk, text="Register", command=register)
    pay_button = tk.Button(start_tk, text="Pay", command=pay)
    login_button = tk.Button(start_tk, text="Login", command=login)

    register_button.grid(row=1, column=0, columnspan=2)
    pay_button.grid(row=3, column=0, columnspan=2)
    login_button.grid(row=4, column=0, columnspan=2)

    start_tk.protocol("WM_DELETE_WINDOW", end_tk)

    start_tk.mainloop()

def send_player_input(client):
    keys = pygame.key.get_pressed()
    input_data = ({
        'left': keys[pygame.K_LEFT],
        'right': keys[pygame.K_RIGHT],
        'up': keys[pygame.K_UP],
        'down': keys[pygame.K_DOWN],
    })
    client.send(pickle.dumps(input_data))

def receive_game_state(client):
    try:
        data = recv_msg(client)
        return data
    except Exception as e:
        print(f"Error receiving game state: {e}")
        return None

def render_players_scores(game_state):
    font = pygame.font.Font('freesansbold.ttf', 24)
    y_offset = 10
    for player_id, (player_x, player_y) in game_state['players'].items():
        score = game_state['player_scores'].get(player_id, 0)
        text = font.render(f"Player-{player_id + 1}: {score}", True, game_state['color'][player_id])
        screen.blit(text, (10, y_offset))
        y_offset += 30

def disconnect_server(client: socket.socket, recv_from: str):
    global connected
    connected = False
    client.send(pickle.dumps(DISCONNECT_MESSAGE))
    if recv_from == "client":
        print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    elif recv_from == "server":
        print(f"[DISCONNECTED] Server disconnected from Client.")
    client.close()

def recv_msg(client: socket.socket, disconnect_info: str = ""):
    msg = client.recv(SIZE)
    if not msg:
        return ''
    msg = pickle.loads(msg)
    if msg == DISCONNECT_MESSAGE:
        print(disconnect_info)
        disconnect_server(client, "server")
    return msg

try:
    if __name__ == "__main__":
        client.connect(ADDR)
        print(f"> [CONNECTED] Client connected to server at {IP}:{PORT}")

        game_entry()

        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Coin Collector Game")

        connected, iteration = True, 0
        while connected:    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    client.send(pickle.dumps("QUIT"))
                    connected = False

            if iteration == 0:
                client.send(pickle.dumps("QUEUE"))
            if not IN_QUEUE:
                send_player_input(client)
            game_state = receive_game_state(client)
            
            if type(game_state) in (int, str):
                iteration = 1
                if game_state == "TIMEOUT":
                    font = pygame.font.Font('freesansbold.ttf', 32)
                    countdown_text = f"Disconnecting from server in {countdown} sec"
                    countdown_start_time = pygame.time.get_ticks()
                    clock = pygame.time.Clock()
                    while countdown > 0:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                        current_time = pygame.time.get_ticks()
                        elapsed_time = current_time - countdown_start_time
                        # Update countdown text every second
                        if elapsed_time >= 1000:
                            countdown -= 1
                            countdown_text = f"Disconnecting from server in {countdown} sec"
                            countdown_start_time = current_time
                        screen.fill((0, 0, 0))  # Clear the screen
                        text_surface = font.render(countdown_text, True, (255, 255, 255))
                        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - text_surface.get_height() // 2))
                        font = pygame.font.Font('freesansbold.ttf', 32)
                        text = font.render(f'Your Time is Out!', True, (255, 255, 255))
                        textRect = text.get_rect()
                        textRect.center = (WIDTH // 2, HEIGHT // 2 - 50)
                        screen.blit(text, textRect)
                        pygame.display.flip()
                        clock.tick(60)
                if game_state == "QUEUE":
                    font = pygame.font.Font('freesansbold.ttf', 32)
                    text = font.render(f'Players are full!', True, (255, 255, 255))
                    textRect = text.get_rect()
                    textRect.center = (WIDTH // 2, HEIGHT // 2)
                    screen.blit(text, textRect)
                    text1 = font.render(f'Wait till your chance comes', True, (255, 255, 255))
                    textRect = text1.get_rect()
                    textRect.center = (WIDTH // 2, HEIGHT // 2 + 50)
                    screen.blit(text1, textRect)
                    pygame.display.flip()
                    client.send(pickle.dumps("QUEUE"))
            else:
                if game_state != None:
                    IN_QUEUE = False
                    iteration = 1
                    coins = game_state['coins']
                    
                    screen.fill(BACKGROUND) 

                    for player_id, (player_x, player_y) in game_state['players'].items():
                        player_color = game_state['color'][player_id]
                        pygame.draw.rect(screen, player_color, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
                    for coin_x, coin_y in coins:                                
                        pygame.draw.ellipse(screen, COIN_COLOR, (coin_x, coin_y, COIN_SIZE, COIN_SIZE))

                    render_players_scores(game_state)
                    pygame.display.flip()

        pygame.quit()
except KeyboardInterrupt:
    client.send(pickle.dumps(DISCONNECT_MESSAGE))
    os._exit(1)

