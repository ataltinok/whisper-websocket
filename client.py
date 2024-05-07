# Client

import asyncio
import websockets

async def main():

    uri = "ws://13.49.225.94:80"
    async with websockets.connect(uri) as websocket:
        while True:
            print("Connection successful.")
            message = input("What do you want to say? (Enter \'quit\' to exit)\n")
            if message=="quit": break
            await websocket.send(message)
            print("Message sent")

            confirm = await websocket.recv()
            print(confirm)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("User interrupted")

