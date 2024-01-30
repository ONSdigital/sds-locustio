from google.cloud import firestore

@firestore.transactional
def perform_delete_transaction(
    transaction: firestore.Transaction, collection_ref: firestore.CollectionReference, survey_id: str
):
    _delete_collection(transaction, collection_ref, survey_id)


def _delete_collection(
    transaction: firestore.Transaction, collection_ref: firestore.CollectionReference, survey_id: str
) -> None:
    """
    Recursively deletes the collection and its subcollections.
    Parameters:
    collection_ref (firestore.CollectionReference): the reference of the collection being deleted.
    """
    doc_collection = collection_ref.where("survey_id", "==", survey_id).stream()

    for doc in doc_collection:
        _recursively_delete_document_and_sub_collections(transaction, doc.reference, survey_id)


def _recursively_delete_document_and_sub_collections(
    transaction: firestore.Transaction,
    doc_ref: firestore.DocumentReference,
    survey_id: str,
) -> None:
    """
    Loops through each collection in a document and deletes the collection.
    Parameters:
    doc_ref (firestore.DocumentReference): the reference of the document being deleted.
    """
    for collection_ref in doc_ref.collections():
        _delete_collection(transaction, collection_ref, survey_id)

    transaction.delete(doc_ref)