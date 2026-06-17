from typing import TypedDict

from configs import endpoints_func
from configs.config import App, config


class EndpointConfig(TypedDict):
    url: str # URL path of the endpoint, excluding base URL
    method: str # HTTP method (GET, POST, PUT, etc.)
    name: str # Group name to group endpoint with different parameters calling into the same test method in result
    params: dict[str, str | dict] | None # URL parameters to be sent with the request, with optional placeholders for runtime values
    payload: str | None # File path for the payload to be sent with the request, if applicable

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
POST_CI: str = "post_ci_schema"
PUT_VALIDATOR_VERSION: str = "put_validator_version"

# Runtime value placeholders
RUNTIME_DATASET_ID_PLACEHOLDER = "dataset_id_placeholder"
RUNTIME_SCHEMA_ID_PLACEHOLDER = "schema_guid_placeholder"


SDS_ENDPOINTS: dict[str, EndpointConfig] = {
    GET_SCHEMA_METADATA: {
        "url": "/v1/schema_metadata",
        "method": "GET",
        "name": "/v1/schema_metadata?survey_id=[survey_id]",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
        },
        "payload": None,
    },
    GET_SCHEMA: {
        "url": "/v1/schema",
        "method": "GET",
        "name": "/v1/schema?survey_id=[survey_id]",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
        },
        "payload": None,
    },
    GET_SCHEMA_V2: {
        "url": "/v2/schema",
        "method": "GET",
        "name": "/v2/schema?guid=[guid]",
        "params": {
            "guid": RUNTIME_SCHEMA_ID_PLACEHOLDER,
        },
        "payload": None,
    },
    GET_DATASET_METADATA: {
        "url": "/v1/dataset_metadata",
        "method": "GET",
        "name": "/v1/dataset_metadata?survey_id=[survey_id]&period_id=[period_id]",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
            "period_id": config.TEST_PERIOD_ID,
        },
        "payload": None,
    },
    GET_UNIT_DATA: {
        "url": "/v1/unit_data",
        "method": "GET",
        "name": "/v1/unit_data?dataset_id=[dataset_id]&identifier=[identifier]",
        "params": {
            "dataset_id": RUNTIME_DATASET_ID_PLACEHOLDER,
            "identifier": config.TEST_UNIT_DATA_IDENTIFIER,
        },
        "payload": None,
    },
    GET_SURVEY_LIST: {
        "url": "/v1/survey_list",
        "method": "GET",
        "name": "/v1/survey_list",
        "params": None,
        "payload": None,
    }
}


CIR_ENDPOINTS: dict[str, EndpointConfig] = {
    POST_CI: {
        "url": "/collection-instruments",
        "method": "POST",
        "name": "/collection-instruments?guid=[guid]&validator_version=[validator_version]",
        "params": {
            "guid": {
                "value": config.TEST_CI_GUID,
                "function": endpoints_func.generate_unique_value,
            },
             "validator_version": config.TEST_CI_VALIDATOR_VERSION,
        },
        "payload": config.TEST_CI_SCHEMA_FILE,
    },
    GET_CI_METADATA: {
        "url": "/collection-instruments/metadata",
        "method": "GET",
        "name": "/collection-instruments/metadata?survey_id=[survey_id]&language=[language]&classifier_type=[classifier_type]&classifier_value=[classifier_value]",
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
            "language": config.TEST_CI_LANGUAGE,
            "classifier_type": config.TEST_CI_CLASSIFIER_TYPE,
            "classifier_value": config.TEST_CI_CLASSIFIER_VALUE,
        },
        "payload": None,
    },
    GET_CI_SCHEMA: {
        "url": "/collection-instruments/schema",
        "method": "GET",
        "name": "/collection-instruments/schema?guid=[guid]",
        "params": {
            "guid": config.TEST_CI_GUID,
        },
        "payload": None,
    },
    PUT_VALIDATOR_VERSION: {
        "url": "/collection-instruments/validator-version",
        "method": "PUT",
        "name": "/collection-instruments/validator-version?guid=[guid]&validator_version=[validator_version]",
        "params": {
            "guid": config.TEST_CI_GUID,
            "validator_version": {
                "value": None,
                "function": endpoints_func.generate_unique_validator_version,
            },
        },
        "payload": config.TEST_CI_SCHEMA_FILE,
    },
}

ALL_ENDPOINTS: dict[str, EndpointConfig] = {**SDS_ENDPOINTS, **CIR_ENDPOINTS}

SDS_ENDPOINTS_CHOICE: list = ["all"] + list(SDS_ENDPOINTS.keys())
CIR_ENDPOINTS_CHOICE: list = ["all"] + list(CIR_ENDPOINTS.keys())

SDS_ENDPOINTS_DEFAULT: str = GET_UNIT_DATA
CIR_ENDPOINTS_DEFAULT: str = GET_CI_METADATA

ENDPOINTS_CONFIG = {
    App.SDS: {
        "test_endpoints": SDS_ENDPOINTS,
        "test_endpoints_choice": SDS_ENDPOINTS_CHOICE,
        "test_endpoints_default": SDS_ENDPOINTS_DEFAULT,
    },
    App.CIR: {
        "test_endpoints": CIR_ENDPOINTS,
        "test_endpoints_choice": CIR_ENDPOINTS_CHOICE,
        "test_endpoints_default": CIR_ENDPOINTS_DEFAULT,
    },
}
