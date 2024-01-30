from firebase_admin import firestore
from config import config


class FirebaseLoader:
    def __init__(self):
        self.client = self._connect_client()

    def get_client(self) -> firestore.Client:
        """
        Get the firestore client
        """
        return self.client

    def _connect_client(self) -> firestore.Client:
        """
        Connect to the firestore client using PROJECT_ID
        """
        return firestore.Client(
            project=config.PROJECT_ID, database=config.PROJECT_ID + "-" + config.DATABASE)


firebase_loader = FirebaseLoader()
