import argparse
import logging

from google.cloud import scheduler_v1

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Force running schedule job to publish dataset...")

    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="ID of project")
    args = parser.parse_args()

    # Check if the required arguments are given
    if not args.project_id:
        logging.error("No project_id is given to delete data")
        exit()

    client = scheduler_v1.CloudSchedulerClient()

    request = scheduler_v1.RunJobRequest(
        name=f"projects/{args.project_id}/locations/europe-west2/jobs/trigger-new-dataset"
    )

    client.run_job(request=request)

    logger.info("Schedule job run completed")
