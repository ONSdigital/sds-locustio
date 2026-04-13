from config_helpers import get_value_from_env


class Config:
    CONF = get_value_from_env("CONF", "default")
    BASE_URL = get_value_from_env("BASE_URL", "http://127.0.0.1:3033")
    PROJECT_ID = get_value_from_env("PROJECT_ID", "ons-sds-sandbox-01")
    TEST_SCHEMA_FILE = "test_schema/schema.json"
    TEST_DATASET_FILE = "test_dataset/generated_data.json"
    UNIT_DATA_FILE = "test_dataset/unit_data.txt"
    OAUTH_CLIENT_ID = get_value_from_env(
        "OAUTH_CLIENT_ID",
        "default",
    )
    DATABASE = get_value_from_env("DATABASE", "sds")
    FIXED_IDENTIFIERS = ["43532", "65871"]


config = Config()
