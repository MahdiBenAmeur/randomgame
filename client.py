# client_ws.py
import asyncio
import websockets
import threading
import pygame
import time
import sys

# === WebSocket Configuration ===
# Replace with your WebSocket URI. For example, if using ngrok HTTP tunnel:
# WS_URI = "ws://<your-ngrok-subdomain>.ngrok.io"
WS_URI = "https://f66b-102-159-5-65.ngrok-free.app"  # for local testing

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

# Define border dimensions
BORDER_LEFT = 0
BORDER_RIGHT = SCREEN_WIDTH
BORDER_TOP = 0
BORDER_BOTTOM = SCREEN_HEIGHT

# Global dictionary for players
# Each entry: name: [player_image, player_rect, text, text_rect, facing_right]
players = {}

def Spawn(name):
    try:
        player_image = pygame.image.load("images/player.png").convert_alpha()
    except Exception as e:
        print("Error loading player image:", e)
        # Fallback: create a simple surface if image load fails
        player_image = pygame.Surface((50, 50))
        player_image.fill((255, 255, 255))
    player_rect = player_image.get_rect(center=STARTING_POSITION)
    text = font.render(name, True, (255, 255, 255))
    text_rect = text.get_rect(center=(player_rect.centerx, player_rect.top - 10))
    players[name] = [player_image, player_rect, text, text_rect, True]  # True = facing right
    # Reset positions for all players (if needed)
    for pname in players:
        players[pname][1].center = STARTING_POSITION
        players[pname][3].center = (players[pname][1].centerx, players[pname][1].top - 10)

# === WebSocket Client Setup ===
ws_connection = None  # Will store the active WebSocket connection
ws_loop = None       # The asyncio event loop running in a separate thread

async def ws_handler():
    """
    Async function to manage the WebSocket connection.
    """
    global ws_connection, NAME
    try:
        async with websockets.connect(WS_URI) as websocket:
            ws_connection = websocket
            print("[+] Connected to WebSocket server")
            # Wait for initial message (for example, the number of players)
            init_data = await websocket.recv()
            try:
                count = int(init_data)
                # Spawn players named "1", "2", ... based on count
                for i in range(count):
                    Spawn(str(i + 1))
                # Set local player's name to "1" (or choose another logic as needed)
                NAME = "1"
            except ValueError:
                # If not an int, treat the data as the player's name
                NAME = init_data
                Spawn(NAME)

            # Now, continuously receive messages from the server
            async for message in websocket:
                # Message format expected: "direction,name;" (possibly multiple commands separated by ;)
                instructions = message.split(";")
                for instruction in instructions:
                    if not instruction:
                        continue
                    try:
                        direction, pname = instruction.split(",")
                        if pname not in players:
                            # If new player, spawn them
                            Spawn(pname)
                        if direction == "left":
                            if players[pname][4]:  # if currently facing right
                                players[pname][0] = pygame.transform.flip(players[pname][0].copy(), True, False)
                            players[pname][4] = False
                            players[pname][1].x -= 5
                        elif direction == "right":
                            if not players[pname][4]:  # if currently facing left
                                players[pname][0] = pygame.transform.flip(players[pname][0].copy(), True, False)
                            players[pname][4] = True
                            players[pname][1].x += 5
                        # Clamp positions
                        players[pname][1].x = max(BORDER_LEFT, min(players[pname][1].x, BORDER_RIGHT - players[pname][1].width))
                        players[pname][3].center = (players[pname][1].centerx, players[pname][1].top - 10)
                    except Exception as e:
                        print(f"[!] Error processing instruction '{instruction}':", e)
                await asyncio.sleep(0.01)
    except Exception as e:
        print("[!] WebSocket connection error:", e)

def start_ws_loop():
    """
    Start the asyncio event loop for the WebSocket connection in a separate thread.
    """
    global ws_loop
    ws_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(ws_loop)
    ws_loop.run_until_complete(ws_handler())

# Start the WebSocket handler in a daemon thread.
ws_thread = threading.Thread(target=start_ws_loop, daemon=True)
ws_thread.start()

# A helper function to send messages via WebSocket from the main (pygame) thread.
def send_ws_message(message):
    if ws_connection is not None and ws_loop is not None:
        # Schedule the coroutine in the ws_loop from the main thread.
        asyncio.run_coroutine_threadsafe(ws_connection.send(message), ws_loop)

# === Pygame Main Loop ===
# If the ws_handler hasn't finished initializing, wait a short moment.
time.sleep(1)
if not players:
    # If no players were spawned, assume this client is alone and set a default name.
    NAME = "1"
    Spawn(NAME)
else:
    # Otherwise, pick the first player's name as our local name.
    NAME = list(players.keys())[0]

def goLeft():
    if players[NAME][1].left > BORDER_LEFT:
        send_ws_message(f"left,{NAME};")

def goRight():
    if players[NAME][1].right < BORDER_RIGHT:
        send_ws_message(f"right,{NAME};")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        goLeft()
        if players[NAME][4]:  # If facing right, flip to left
            players[NAME][0] = pygame.transform.flip(players[NAME][0].copy(), True, False)
            players[NAME][4] = False
        players[NAME][1].x -= 5

    if keys[pygame.K_RIGHT]:
        goRight()
        if not players[NAME][4]:  # If facing left, flip to right
            players[NAME][0] = pygame.transform.flip(players[NAME][0].copy(), True, False)
            players[NAME][4] = True
        players[NAME][1].x += 5

    # Keep the player within the borders
    players[NAME][1].x = max(BORDER_LEFT, min(players[NAME][1].x, BORDER_RIGHT - players[NAME][1].width))
    players[NAME][3].center = (players[NAME][1].centerx, players[NAME][1].top - 10)

    # Render everything
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
