import asyncio
import websockets


async def test():
    async with websockets.connect('ws://localhost:1234') as websocket:
        await websocket.send("hello websocket")
        users_connected = await websocket.recv()
        print(users_connected)
        response = await websocket.recv()
        print(response)

        #remove_response = await websocket.recv()
        #print(remove_response)

asyncio.get_event_loop().run_until_complete(test())