from enum import StrEnum

from configs.config_helpers import get_value_from_env

from locust_test import FIXED_IDENTIFIERS, LOCUST_TEST_ID


class App(StrEnum):
    SDS = "sds"
    CIR = "cir"


class Config:
    APP: App = get_value_from_env("APP", "sds") # Can be set to "sds" or "cir" to specify which application to test
    BASE_URL = get_value_from_env("BASE_URL", "http://127.0.0.1:3033") # Base URL for the application under test. Require https://
    PROJECT_ID = get_value_from_env("PROJECT_ID", "ons-sds-sandbox-01")
    TEST_SCHEMA_FILE = "test_schema/schema.json"
    TEST_DATASET_FILE = "test_dataset/generated_data.json"
    TEST_CI_SCHEMA_FILE = "test_schema/ci_schema.json"
    UNIT_DATA_FILE = "test_dataset/unit_data.txt"
    OAUTH_CLIENT_ID = get_value_from_env(
        "OAUTH_CLIENT_ID",
        "default",
    )
    TEST_UNIT_DATA_IDENTIFIER = FIXED_IDENTIFIERS[0]
    TEST_SURVEY_ID = LOCUST_TEST_ID
    TEST_PERIOD_ID = LOCUST_TEST_ID
    TEST_CI_GUID = LOCUST_TEST_ID

config = Config()
