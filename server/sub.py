import asyncio
import os

import websockets
from google.cloud import pubsub

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
proj_name = 'pcd2-272020'
sub_name = 'test'


def callback(message):
    import time
    ts = int(time.time())
    f = open("temp/message-" + str(ts) + ".txt", "a")
    f.write(message.data.decode("utf-8"))
    f.close()

    message.ack()


def get_messages():
    import glob
    files = glob.glob("temp/*.txt")
    messages = []
    for file in files:
        f = open(file, "r")
        messages.append(f.read())
        f.close()
        import os
        os.remove(file)
    return messages


async def send_messages_to_clients(websocket):
    messages = get_messages()
    for message in messages:
        await websocket.send('Received message: {}'.format(message))


async def sub_pull(websocket, path):
    subscriber = pubsub.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        proj_name, sub_name)

    subscriber.subscribe(subscription_path, callback=callback)
    print('Listening for messages on: {}'.format(subscription_path))
    while True:
        await send_messages_to_clients(websocket)


"""
Client awaiting for Google PUB/Sub messages
"""
start_server = websockets.serve(sub_pull, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
