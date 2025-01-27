import socket
import threading
import sys

HOST = '192.168.1.12'  # match the server's HOST
PORT = 5001         # match the server's PORT
NAME = None
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
            direction , name= data.decode('utf-8').split(",")

            if direction == "left":
                #other user went left , update him
                pass
            elif direction=="right":
                #otherplayer went right , update him
                pass
            else :
                #spawn the new player
                pass


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
receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
receiver_thread.start()

def goLeft():
    client_socket.send(f"left,{NAME}")
def goRight():
    client_socket.send(f"right,{NAME}")

