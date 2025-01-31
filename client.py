# client_ws.py
import asyncio
import websockets
import threading
import pygame
import time
import sys

# === WebSocket Configuration ===
WS_URI = "wss://f66b-102-159-5-65.ngrok-free.app"

# === Pygame Initialization ===
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
STARTING_POSITION = (100, 290)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Game")
font = pygame.font.Font(None, 36)

try:
    background = pygame.image.load('images/Background.jpeg').convert()
except Exception as e:
    print("Error loading background image:", e)
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((0, 0, 0))

BORDER_LEFT = 0
BORDER_RIGHT = SCREEN_WIDTH
BORDER_TOP = 0
BORDER_BOTTOM = SCREEN_HEIGHT

players = {}

def Spawn(name):
    try:
        player_image = pygame.image.load("images/player.png").convert_alpha()
    except Exception as e:
        print("Error loading player image:", e)
        player_image = pygame.Surface((50, 50))
        player_image.fill((255, 255, 255))
    player_rect = player_image.get_rect(center=STARTING_POSITION)
    text = font.render(name, True, (255, 255, 255))
    text_rect = text.get_rect(center=(player_rect.centerx, player_rect.top - 10))
    players[name] = [player_image, player_rect, text, text_rect, True]

ws_connection = None
ws_loop = None

async def ws_handler():
    global ws_connection, NAME
    try:
        async with websockets.connect(WS_URI) as websocket:
            ws_connection = websocket
            print("[+] Connected to WebSocket server")
            init_data = await websocket.recv()

            try:
                count = int(init_data)

                for i in range(count):
                    Spawn(str(i + 1))
                print(init_data)
                NAME = init_data
            except ValueError:
                NAME = init_data
                Spawn(NAME)
            async for message in websocket:
                instructions = message.split(";")
                for instruction in instructions:
                    if not instruction:
                        continue
                    try:
                        direction, pname = instruction.split(",")
                        if pname not in players:
                            Spawn(pname)
                        if direction == "left":
                            if players[pname][4]:
                                players[pname][0] = pygame.transform.flip(players[pname][0].copy(), True, False)
                            players[pname][4] = False
                            players[pname][1].x -= 5
                        elif direction == "right":
                            if not players[pname][4]:
                                players[pname][0] = pygame.transform.flip(players[pname][0].copy(), True, False)
                            players[pname][4] = True
                            players[pname][1].x += 5
                        players[pname][1].x = max(BORDER_LEFT, min(players[pname][1].x, BORDER_RIGHT - players[pname][1].width))
                        players[pname][3].center = (players[pname][1].centerx, players[pname][1].top - 10)
                    except Exception as e:
                        print(f"[!] Error processing instruction '{instruction}':", e)
                await asyncio.sleep(0.01)
    except Exception as e:
        print("[!] WebSocket connection error:", e)

def start_ws_loop():
    global ws_loop
    ws_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(ws_loop)
    ws_loop.run_until_complete(ws_handler())

ws_thread = threading.Thread(target=start_ws_loop, daemon=True)
ws_thread.start()

time.sleep(1)
"""if not players:
    NAME = "1"
    Spawn(NAME)
else:
    NAME = list(players.keys())[0]"""

def send_ws_message(message):
    if ws_connection is not None and ws_loop is not None:
        asyncio.run_coroutine_threadsafe(ws_connection.send(message), ws_loop)

def goLeft():
    if players[NAME][1].left > BORDER_LEFT:
        send_ws_message(f"left,{NAME};")
        if players[NAME][4]:
            players[NAME][0] = pygame.transform.flip(players[NAME][0].copy(), True, False)
            players[NAME][4] = False
        players[NAME][1].x -= 5

def goRight():
    if players[NAME][1].right < BORDER_RIGHT:
        send_ws_message(f"right,{NAME};")
        if not players[NAME][4]:
            players[NAME][0] = pygame.transform.flip(players[NAME][0].copy(), True, False)
            players[NAME][4] = True
        players[NAME][1].x += 5

running = True
while running:
    print(NAME)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        goLeft()
    if keys[pygame.K_RIGHT]:
        goRight()
    players[NAME][1].x = max(BORDER_LEFT, min(players[NAME][1].x, BORDER_RIGHT - players[NAME][1].width))
    players[NAME][3].center = (players[NAME][1].centerx, players[NAME][1].top - 10)
    screen.blit(background, (0, 0))
    border_color = (255, 0, 0)
    pygame.draw.rect(screen, border_color, (BORDER_LEFT, BORDER_TOP, SCREEN_WIDTH, SCREEN_HEIGHT), 3)
    for pname, (player_image, player_rect, text, text_rect, _) in players.items():
        screen.blit(player_image, player_rect)
        screen.blit(text, text_rect)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()