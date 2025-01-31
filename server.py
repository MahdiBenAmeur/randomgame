# server_ws.py
import asyncio
import websockets

# A set to keep track of connected clients
connected_clients = set()

async def broadcast(message, sender=None):
    """
    Send a message to all connected clients except the sender.
    """
    if connected_clients:
        await asyncio.gather(*[
            client.send(message)
            for client in connected_clients
            if client != sender
        ])

async def handle_client(websocket, path):
    """
    Handle an incoming client connection.
    """
    print(f"[+] New connection from {websocket.remote_address}")
    connected_clients.add(websocket)

    # For example, on new connection send the number of connected clients
    try:
        # Send the total count as an initial message (so the client can spawn players)
        await websocket.send(str(len(connected_clients)))
    except Exception as e:
        print(f"[!] Error sending initial data: {e}")

    try:
        async for message in websocket:
            # When a message is received, broadcast it to others
            print(f"Received from {websocket.remote_address}: {message}")
            await broadcast(message, sender=websocket)
    except websockets.ConnectionClosed:
        print(f"[-] Connection closed by {websocket.remote_address}")
    except Exception as e:
        print(f"[!] Error with {websocket.remote_address}: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"[!] {websocket.remote_address} disconnected.")

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8000):
        print("[*] WebSocket server listening on port 8000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
