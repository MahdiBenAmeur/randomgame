import socket
import threading
import sys
import pygame

HOST = '192.168.1.12'  # match the server's HOST
PORT = 5001         # match the server's PORT
NAME = None
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
STARTING_POSITION = (100, 290)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Game")
font = pygame.font.Font(None, 36)
background = pygame.image.load('images/Background.jpeg').convert()

players={}

def Spawn(name):
    player_image = pygame.image.load("images/player.png").convert()
    player_rect = player_image.get_rect()
    text = font.render(name, True, (255, 255, 255))
    text_rect = text.get_rect()

    players[name] = (player_image, player_rect, text, text_rect ,True)
    for name, (player_image, player_rect, text, text_rect) in players.items():
        player_rect.center = STARTING_POSITION
        text_rect.center = (player_rect.centerx, player_rect.top - 10)
def receive_messages(client_socket):
    """
    Continuously listen for messages from the server and print them.
    """
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                # Server closed connection
                print("[!] Server closed connection.")
                break
            direction , name = data.decode('utf-8').split(",")

            if direction == "left":
                #other user went left , update him
                if players[name][4]:
                    players[name][0] = pygame.transform.flip(players[name][0], True, False)
                    players[name][4] = not players[name][4]
                players[name][1].x -= 5
                players[name][3].x -= 5
            elif direction=="right":
                #otherplayer went right , update him
                if not players[NAME][4]:
                    players[name][0] = pygame.transform.flip(players[name][0], True, False)
                    players[name][4] = not players[name][4]
                players[name][1].x += 5
                players[name][3].x += 5
            else :
                #spawn the new player
                Spawn(name)


        except ConnectionResetError:
            print("[!] Connection forcibly closed by the server.")
            break
        except Exception as e:
            print(f"[!] Error receiving data: {e}")
            break

    # Once we break out of the loop, close the socket and exit
    client_socket.close()
    sys.exit(0)


# Create a TCP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((HOST, PORT))
    print(f"[+] Connected to server at {HOST}:{PORT}")
except ConnectionRefusedError:
    print("[!] Could not connect to the server. Is it running?")
    sys.exit(1)
except Exception as e:
    print(f"[!] Error connecting to server: {e}")
    sys.exit(1)
# Start a thread to listen for incoming messages
data = client_socket.recv(1024)
NAME= int(data.decode("uft-8"))
Spawn(NAME)
receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
receiver_thread.start()

def goLeft():
    client_socket.send(f"left,{NAME}")
def goRight():
    client_socket.send(f"right,{NAME}")

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        goLeft()
        if players[NAME][4]:
            players[NAME][0] = pygame.transform.flip(players[NAME][0], True, False)
            players[NAME][4] = not players[NAME][4]
        players[NAME][1].x -= 5
        players[NAME][3].x -= 5
    if keys[pygame.K_RIGHT]:
        goRight()
        if not players[NAME][4]:
            players[NAME][0] = pygame.transform.flip(players[NAME][0], True, False)
            players[NAME][4] = not players[NAME][4]
        players[NAME][1].x += 5
        players[NAME][3].x += 5

    screen.blit(background, (0, 0))
    for name, (player_image, player_rect, text, text_rect) in players.items():
        screen.blit(player_image, player_rect)
        screen.blit(text, text_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()