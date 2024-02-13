from config_helpers import get_value_from_env


class Config:
    BASE_URL = get_value_from_env("BASE_URL", "http://127.0.0.1:3033")
    PROJECT_ID = get_value_from_env("PROJECT_ID", "ons-sds-sandbox-01")
    TEST_SCHEMA_FILE = "schema.json"
    TEST_DATASET_FILE = "generated_data.json"
    OAUTH_CLIENT_ID = get_value_from_env(
        "OAUTH_CLIENT_ID",
        "localhost",
    )
    DATABASE = get_value_from_env("DATABASE", "sds")
    DATASET_ENTRIES = get_value_from_env("DATASET_ENTRIES", "1000")
    FIXED_IDENTIFIERS = ["43532", "65871"]


config = Config()
