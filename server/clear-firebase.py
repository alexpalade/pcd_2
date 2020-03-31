import argparse
import json

import google
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

if __name__ == "__main__":
        #parser = argparse.ArgumentParser(description='Chat application server')
        #parser.add_argument('--port', '-p', default=9000, help='which port to listen at')

        #args = parser.parse_args()

        # initialize Firebase
        cred = credentials.Certificate('/home/alexpalade/firebase-credentials.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        db.collection(u'metadata').document(u'counters').delete()
        delete_collection(db.collection(u'chat-history'), 10)
