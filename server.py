import asyncio
import websockets

connected_clients = set()

async def broadcast(message, sender=None):
    if connected_clients:
        await asyncio.gather(*[
            client.send(message)
            for client in connected_clients
            if client != sender
        ], return_exceptions=True)

async def handle_client(websocket):  # Keep 'path' here
    print(f"[+] New connection from {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        await websocket.send(str(len(connected_clients)))
    except Exception as e:
        print(f"[!] Error sending initial data to {websocket.remote_address}: {e}")
    try:
        async for message in websocket:
            print(f"Received from {websocket.remote_address}: {message}")
            await broadcast(message, sender=websocket)
    except Exception as e:
        print(f"[!] Exception for {websocket.remote_address} during message processing: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"[!] {websocket.remote_address} disconnected.")

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8000):
        print("[*] WebSocket server listening on port 8000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())