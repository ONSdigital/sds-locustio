import json
import logging
import random
from pathlib import Path

from configs.config import config

logger = logging.getLogger(__name__)

MIN_DATASET_ENTRIES = 10
MAX_DATASET_ENTRIES = 90000


class JsonGenerator:
    def __init__(
        self,
        survey_id: str,
        file_name: str,
        fixed_identifiers: list[str],
    ):
        self.survey_id = survey_id
        self.file_name = file_name
        self.fixed_identifiers = fixed_identifiers
        self.unit_data_from_str = None

    def generate_dataset_file(self, dataset_entries: int) -> int:
        """
        Generate the dataset file.
        """
        if dataset_entries < MIN_DATASET_ENTRIES or dataset_entries > MAX_DATASET_ENTRIES:
            raise ValueError("dataset_entries must be between 10 and 90000")

        try:
            if not Path(self.file_name).is_file():
                json_data = self._generate_json_data(
                    dataset_entries, self.survey_id, self.fixed_identifiers
                )

                # Write the JSON data to a file
                with open(self.file_name, "w") as json_file:
                    json.dump(json_data, json_file, indent=2)

                logging.info(f"Data successfully written to {self.file_name}")

            return 0
        except Exception as e:
            logging.error(f"Error generating dataset file: {e}")
            return -1


    def _generate_json_data(
        self, dataset_entries: int, survey_id: str, fixed_identifiers: list[str]
    ) -> dict[str, any]:
        """
        Generate the JSON data for the dataset file.

        Args:
            dataset_entries (int): the number of unit data entries to generate
            survey_id (str): the survey id (locust test id)
            fixed_identifiers (list[str]): the list of fixed identifiers

        Returns:
            dict[str, any]: the JSON data for the dataset file
        """
        data = {
            "survey_id": survey_id,
            "period_id": survey_id,
            "form_types": ["0001"],
            "schema_version": "v1.0.0",
            "data": [],
        }

        unique_ids = set()
        working_fixed_identifiers = fixed_identifiers.copy()
        for _ in range(dataset_entries):
            working_fixed_identifiers, identifier = self._generate_unique_identifier(
                unique_ids, working_fixed_identifiers
            )
            unique_ids.add(identifier)
            unit_data = self._generate_unit_data()
            data["data"].append({"identifier": identifier, "unit_data": unit_data})

        return data

    def _generate_unique_identifier(
        self, existing_ids: set[str], working_fixed_identifiers: list[str]
    ) -> tuple[list[str], str]:
        """
        Generate a unique identifier for the dataset file.

        Args:
            existing_ids (set[str]): the set of existing identifiers
            fixed_identifiers (list[str]): the list of fixed identifiers

        Returns:
            tuple[list[str], str]: the updated list of fixed identifiers and the generated identifier
        """
        while True:
            identifier = (
                working_fixed_identifiers.pop()
                if working_fixed_identifiers
                else str(random.randint(10000, 99999))
            )
            if identifier not in existing_ids:
                return working_fixed_identifiers, identifier

    def _generate_unit_data(self) -> str:
        """
        Generate the unit data content for the dataset file.
        """
        # Customize this function to generate whatever unit data you need
        # return "Example data " + str(random.randint(1, dataset_entries))
        if self.unit_data_from_str is not None:
            return self.unit_data_from_str

        with open(config.UNIT_DATA_FILE) as file:
            txt = file.read()
            file.close()

        self.unit_data_from_str = txt

        return txt
