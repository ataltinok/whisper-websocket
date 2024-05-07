# Server
import asyncio
import websockets

async def message_recv(websocket):
    try:
        print("Server is running.")
        while True:
            message = await websocket.recv()
            if message=="quit":
                print("Goodbye")
                break
            print("Message received:",message)

            await websocket.send("We got your message :)")
            print("Sent confirmation")
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection Terminated")


async def main():
    async with websockets.serve(message_recv, "34.77.255.79", 8080):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("User interrupted")

