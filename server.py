import asyncio
import json
import argparse

import websockets

users = set()


# notifica userii ca un user a intrat sau a iesit din aplicatie
# trebuie sa mai lucrez la functia asta
async def notify_users():
        if users:
                message = "New user connected"
                await asyncio.wait([user.send(message) for user in users])


async def send_users_message(message):
        await asyncio.wait([user.send(message) for user in users])


async def register(websocket):
        users.add(websocket)
        #await notify_users()


async def unregister(websocket):
        users.remove(websocket)
        print("Client removed")
        #await notify_users()


async def handle(websocket, path):
        await register(websocket)
        async for message in websocket:
                data = json.loads(message)
                if data["user"] is not None and data["mess"] is None:
                        print("User connected :  ", data["user"])
                        await send_users_message("User " + data["user"] + " now connected.")

                if data["mess"] is not None:
                        print("Message from " + data["user"] + ":" + data["mess"])
                        await send_users_message("Message from " + data["user"] + " : " + data["mess"])

        await unregister(websocket)

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Chat application server')
        parser.add_argument('--port', '-p', default=9000, help='which port to listen at')

        args = parser.parse_args()

        address = "0.0.0.0"

        start_server = websockets.serve(handle, address, args.port)
        print("websockets listening at {}:{}".format(address, args.port))

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
