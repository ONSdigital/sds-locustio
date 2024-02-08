import argparse

from google.cloud import firestore


def delete_firestore_locust_test_data(
    project_id: str, database_name: str, survey_id: str
):
    """
    Function to delete schema and dataset data of the locust test from FireStore database.

    Parameters:
        project_id (str): the project id
        database_name (str): the name of the database
        survey_id (str): the locust test id
    """
    try:
        client = firestore.Client(project=project_id, database=database_name)

        schemas_collection = client.collection("schemas")
        delete_collection_in_batches(schemas_collection, survey_id, 100)
        datasets_collection = client.collection("datasets")
        delete_collection_in_batches(datasets_collection, survey_id, 100)
    except Exception as e:
        print("Failed to delete firestore locust test data")


def delete_collection_in_batches(
    collection_ref: firestore.CollectionReference, survey_id: str, batch_size: int
):
    docs = collection_ref.where("survey_id", "==", survey_id).limit(batch_size).get()
    doc_count = 0

    for doc in docs:
        doc_count += 1
        # Delete all subcollections of document
        for subcollection in doc.reference.collections():
            delete_collection_in_batches(subcollection, survey_id, batch_size)

        doc.reference.delete()

    if doc_count < batch_size:
        return None
        
    return delete_collection_in_batches(collection_ref, survey_id, batch_size)


if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="ID of project")
    parser.add_argument("--database_name", help="Name of FireStore db")
    parser.add_argument("--survey_id", help="key to delete data")
    args = parser.parse_args()

    # Check if the required arguments are given
    if not args.survey_id:
        print("Error. No survey_id is given to delete data")
        exit()
    if not args.project_id:
        print("Error. No project_id is given to delete data")
        exit()
    if not args.database_name:
        print("Error. No database_name is given to delete data")
        exit()

    delete_firestore_locust_test_data(
        args.project_id, args.database_name, args.survey_id
    )
