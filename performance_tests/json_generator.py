import json
import random


class JsonGenerator:
    def __init__(
        self,
        survey_id: str,
        file_name: str,
        dataset_entries: str,
        fixed_identifiers: list[str],
    ):
        self.survey_id = survey_id
        self.file_name = file_name
        self.dataset_entries = dataset_entries
        self.fixed_identifiers = fixed_identifiers

    def generate_dataset_file(self) -> None:
        """
        Generate the dataset file.
        """
        try:
            json_data = self._generate_json_data(
                self.dataset_entries, self.survey_id, self.fixed_identifiers
            )

            # Specify the output file name
            output_file_name = self.file_name

            # Write the JSON data to a file
            with open(output_file_name, "w") as json_file:
                json.dump(json_data, json_file, indent=2)

            print(f"Data successfully written to {output_file_name}")
        except Exception as e:
            print(f"Error generating dataset file: {e}")

    def _generate_json_data(
        self, entries_count: int, survey_id: str, fixed_identifiers: list[str]
    ) -> dict[str, any]:
        """
        Generate the JSON data for the dataset file.

        Args:
            entries_count (int): the number of unit data entries to generate
            survey_id (str): the survey id (locust test id)

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
        for _ in range(entries_count):
            fixed_identifiers, identifier = self._generate_unique_identifier(
                unique_ids, fixed_identifiers
            )
            unique_ids.add(identifier)
            unit_data = self._generate_unit_data()
            data["data"].append({"identifier": identifier, "unit_data": unit_data})

        return data

    def _generate_unique_identifier(
        self, existing_ids: set[str], fixed_identifiers: list[str]
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
                fixed_identifiers.pop()
                if fixed_identifiers
                else str(random.randint(10000, 99999))
            )
            if identifier not in existing_ids:
                return fixed_identifiers, identifier

    def _generate_unit_data(self) -> str:
        """
        Generate the unit data content for the dataset file.
        """
        # Customize this function to generate whatever unit data you need
        return "Example data " + str(random.randint(1, self.dataset_entries))
