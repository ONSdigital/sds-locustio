from typing import TypedDict

from configs.config import config
from preprocess.preprocess_sds_dataset import PreProcessSDSDataset
from preprocess.preprocess_base import PreProcessBase


class EndpointConfig(TypedDict):
    url: str
    method: str
    params: dict[str, str] | None

# SDS Endpoints

GET_UNIT_DATA: str = "get_unit_data"
GET_DATASET_METADATA: str = "get_dataset_metadata"
GET_SCHEMA: str = "get_schema"
GET_SCHEMA_METADATA: str = "get_schema_metadata"
GET_SCHEMA_V2: str = "get_schema_v2"
GET_SURVEY_LIST: str = "get_survey_list"

# CIR Endpoints

## External use endpoints
GET_CI_METADATA: str = "get_ci_metadata"
GET_CI_SCHEMA: str = "get_ci_schema"
GET_CI_VALIDATOR_METADATA: str = "get_ci_validator_metadata"
POST_CI: str = "post_ci"
PUT_VALIDATOR_VERSION: str = "put_validator_version"

# Runtime value placeholders
DATASET_ID_PLACEHOLDER = "dataset_id_placeholder"
SCHEMA_ID_PLACEHOLDER = "schema_guid_placeholder"


SDS_ENDPOINTS: dict[str, EndpointConfig] = {
    GET_SCHEMA_METADATA: {
        "url": "/v1/schema_metadata",
        "method": "GET",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
        }
    },
    GET_SCHEMA: {
        "url": "/v1/schema",
        "method": "GET",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
        }
    },
    GET_SCHEMA_V2: {
        "url": "/v2/schema",
        "method": "GET",
        "params": {
            "guid": SCHEMA_ID_PLACEHOLDER,
        }
    },
    GET_DATASET_METADATA: {
        "url": "/v1/dataset_metadata",
        "method": "GET",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
            "period_id": config.TEST_PERIOD_ID,
        },
    },
    GET_UNIT_DATA: {
        "url": "/v1/unit_data",
        "method": "GET",
        "params": {
            "dataset_id": DATASET_ID_PLACEHOLDER,
            "identifier": config.TEST_UNIT_DATA_IDENTIFIER,
        },
    },
    GET_SURVEY_LIST: {
        "url": "/v1/survey_list",
        "method": "GET",
        "params": None,
    }
}


CIR_ENDPOINTS: dict[str, EndpointConfig] = {
    GET_CI_METADATA: {
        "url": "/collection-instruments/metadata",
        "method": "GET",
        "params": None,
    },
    GET_CI_SCHEMA: {
        "url": "/collection-instruments/schema",
        "method": "GET",
        "params": None,
    },
    GET_CI_VALIDATOR_METADATA: {
        "url": "/collection-instruments/validator-metadata",
        "method": "GET",
        "params": None,
    },
    POST_CI: {
        "url": "/collection-instruments",
        "method": "POST",
        "params": None,
    },
    PUT_VALIDATOR_VERSION: {
        "url": "/collection-instruments/validator-version",
        "method": "PUT",
        "params": None,
    },
}

SDS_ENDPOINTS_CHOICE: list = ["all"] + list(SDS_ENDPOINTS.keys())
CIR_ENDPOINTS_CHOICE: list = ["all"] + list(CIR_ENDPOINTS.keys())

SDS_ENDPOINTS_DEFAULT: str = GET_UNIT_DATA
