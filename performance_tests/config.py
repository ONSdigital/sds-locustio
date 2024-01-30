from config_helpers import get_value_from_env

class Config:
    BASE_URL = get_value_from_env("BASE_URL", "http://127.0.0.1:3000")
    PROJECT_ID = get_value_from_env("PROJECT_ID", "ons-sds-sandbox-01")
    TEST_SCHEMA_FILE = "schema.json"
    TEST_DATASET_FILE = "dataset.json"
    OAUTH_CLIENT_ID = get_value_from_env(
        "OAUTH_CLIENT_ID",
        "localhost",
    )
    DATABASE = "sds"

config = Config()