import asyncio
import json
import argparse

import websockets

import google
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

users = set()

# notifica userii ca un user a intrat sau a iesit din aplicatie
# trebuie sa mai lucrez la functia asta
async def notify_users():
        if users:
                message = "New user connected"
                await asyncio.wait([user.send(message) for user in users])


async def send_users_message(message):
        await asyncio.wait([user.send(message) for user in users])


async def send_user_chat_history(user):
        global index

        backlog_size = 50
        from_index = max(0, index - backlog_size)

        for i in range(from_index, index):
            doc_ref = db.collection(u'chat-history').document(str(i))
            try:
                doc = doc_ref.get().to_dict()

                type = doc['type']

                text = None
                if type == 'message':
                    text = 'Message from {} : {}'.format(doc['user'], doc['message'])
                elif type == 'connected':
                    text = 'User {} now connected.'.format(doc['user'])

                if text:
                    await asyncio.wait([user.send(text)])
            except google.cloud.exceptions.NotFound:
                print('Error while retrieving message index {}'.format(i))

        if index > 0:
            await asyncio.wait([user.send('--- end history (last {}) ---'.format(backlog_size))])


async def register(websocket):
        users.add(websocket)
        await send_user_chat_history(websocket)
        #await notify_users()


async def unregister(websocket):
        users.remove(websocket)
        print("Client removed")
        #await notify_users()


async def handle(websocket, path):
        global db

        await register(websocket)

        async for message in websocket:
                data = json.loads(message)
                if data["user"] is not None and data["mess"] is None:
                        print("User connected :  ", data["user"])
                        log_user_connected(data["user"])
                        await send_users_message("User " + data["user"] + " now connected.")

                if data["mess"] is not None:
                        print("Message from " + data["user"] + ":" + data["mess"])
                        log_message(data["user"], data["mess"])
                        await send_users_message("Message from " + data["user"] + " : " + data["mess"])

        await unregister(websocket)

def log_user_connected(user):
    log_event({
        u'type': u'connected',
        u'user': user,
        })

def log_message(user, message):
    log_event({
        u'type': u'message',
        u'user': user,
        u'message': message,
        })

def log_event(values):
        global index

        doc_ref = db.collection(u'chat-history').document(str(index))
        doc_ref.set(values)

        index += 1
        doc_ref = db.collection(u'metadata').document(u'counters')
        doc_ref.set({ u'index' : index })

if __name__ == "__main__":
        global db
        global index

        parser = argparse.ArgumentParser(description='Chat application server')
        parser.add_argument('--port', '-p', default=9000, help='which port to listen at')

        args = parser.parse_args()

        address = "0.0.0.0"

        start_server = websockets.serve(handle, address, args.port)
        print("websockets listening at {}:{}".format(address, args.port))

        # initialize Firebase
        cred = credentials.Certificate('/home/alexpalade/firebase-credentials.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        doc_ref = db.collection(u'metadata').document(u'counters')

        try:
            doc = doc_ref.get()
            index = int(doc.to_dict()['index'])
        except TypeError:
            index = 0
        except google.cloud.exceptions.NotFound:
            index = 0

        print(u'Starting from message index: {}'.format(index))

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

