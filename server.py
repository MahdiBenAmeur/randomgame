import socket
import threading

# Server Configuration
HOST = '0.0.0.0'  # or '0.0.0.0' to accept connections from any network interface
PORT = 5001         # choose any free port

# This will hold references to all connected client sockets
client_sockets = []

def broadcast(message, sender_socket=None):
    """
    Send a message to all connected clients except the sender (if sender_socket is given).
    """
    for client in client_sockets:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message to a client: {e}")
                # Optionally, you could remove that client from the list

def handle_client(client_socket, address):
    """
    Receive messages from this client and broadcast them to others.
    """
    print(f"[+] New connection from {address}")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                # Client disconnected
                print(f"[-] Connection closed by {address}")
                break
            # Broadcast the received message to other clients
            message_to_send = f"{address}: {data.decode('utf-8')}"
            print(message_to_send)
            broadcast(data, sender_socket=client_socket)

        except ConnectionResetError:
            print(f"[-] Connection forcibly closed by {address}")
            break
        except Exception as e:
            print(f"[!] Error with {address}: {e}")
            break

    # Remove the client_socket from the client list, then close it
    if client_socket in client_sockets:
        client_sockets.remove(client_socket)
    client_socket.close()
    print(f"[!] {address} disconnected.")


def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse the port if possible
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to host and port
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[*] Server listening on {HOST}:{PORT}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_sockets.append(client_socket)
            data=str(len(client_socket)).encode("utf-8")
            client_socket.send(data)
            broadcast(data)
            # Start a new thread to handle each client connection
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    finally:
        # Close all client sockets
        for sock in client_sockets:
            sock.close()
        server_socket.close()

if __name__ == "__main__":
    main()
