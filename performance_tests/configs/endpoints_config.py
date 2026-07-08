from typing import TypedDict

from performance_tests.configs import endpoints_func
from performance_tests.configs.config import App, config


class EndpointConfig(TypedDict):
    url: str # URL path of the endpoint, excluding base URL
    method: str # HTTP method (GET, POST, PUT, etc.)
    name: str # Group name to group endpoint with different parameters calling into the same test method in result
    query_parameters: bool # Whether the endpoint requires query parameters
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

# URL placeholders
PLACEHOLDERS: dict[str, str] = {
    "guid": "{guid}",
    "dataset_id": "{dataset_id}",
    "identifier": "{identifier}",
}

SDS_ENDPOINTS: dict[str, EndpointConfig] = {
    GET_SCHEMA_METADATA: {
        "url": "/schemas/metadata",
        "method": "GET",
        "name": "/schemas/metadata?survey_id=[survey_id]",
        "query_parameters": True,
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
        },
        "payload": None,
    },
    GET_SCHEMA: {
        "url": "/schemas",
        "method": "GET",
        "name": "/schemas?survey_id=[survey_id]",
        "query_parameters": True,
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
        },
        "payload": None,
    },
    GET_SCHEMA_V2: {
        "url": f"/schemas/{PLACEHOLDERS['guid']}",
        "method": "GET",
        "name": f"/schemas/{PLACEHOLDERS['guid']}",
        "query_parameters": False,
        "params": {
            "guid": RUNTIME_SCHEMA_ID_PLACEHOLDER,
        },
        "payload": None,
    },
    GET_DATASET_METADATA: {
        "url": "/datasets/metadata",
        "method": "GET",
        "name": "/datasets/metadata?survey_id=[survey_id]&period_id=[period_id]",
        "query_parameters": True,
        "params": {
            "survey_id": config.TEST_SURVEY_ID,
            "period_id": config.TEST_PERIOD_ID,
        },
        "payload": None,
    },
    GET_UNIT_DATA: {
        "url": f"/datasets/{PLACEHOLDERS['dataset_id']}/unit-data/{PLACEHOLDERS['identifier']}",
        "method": "GET",
        "name": f"/datasets/{PLACEHOLDERS['dataset_id']}/unit-data/{PLACEHOLDERS['identifier']}",
        "query_parameters": False,
        "params": {
            "dataset_id": RUNTIME_DATASET_ID_PLACEHOLDER,
            "identifier": config.TEST_UNIT_DATA_IDENTIFIER,
        },
        "payload": None,
    },
    GET_SURVEY_LIST: {
        "url": "/surveys",
        "method": "GET",
        "name": "/surveys",
        "query_parameters": False,
        "params": None,
        "payload": None,
    }
}


CIR_ENDPOINTS: dict[str, EndpointConfig] = {
    POST_CI: {
        "url": "/collection-instruments",
        "method": "POST",
        "name": "/collection-instruments?guid=[guid]&validator_version=[validator_version]",
        "query_parameters": True,
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
        "query_parameters": True,
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
        "query_parameters": True,
        "params": {
            "guid": config.TEST_CI_GUID,
        },
        "payload": None,
    },
    PUT_VALIDATOR_VERSION: {
        "url": "/collection-instruments/validator-version",
        "method": "PUT",
        "name": "/collection-instruments/validator-version?guid=[guid]&validator_version=[validator_version]",
        "query_parameters": True,
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

SDS_ENDPOINTS_CHOICE: list = ["all", *list(SDS_ENDPOINTS.keys())]
CIR_ENDPOINTS_CHOICE: list = ["all", *list(CIR_ENDPOINTS.keys())]

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
