from typing import TypedDict

class EndpointConfig(TypedDict):
    url: str
    method: str

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


SDS_ENDPOINTS: dict[str, EndpointConfig] = {
    GET_SCHEMA_METADATA: {
        "url": "/v1/schema_metadata",
        "method": "GET",
    },
    GET_SCHEMA: {
        "url": "/v1/schema",
        "method": "GET",
    },
    GET_SCHEMA_V2: {
        "url": "/v2/schema",
        "method": "GET",
    },
    GET_DATASET_METADATA: {
        "url": "/v1/dataset_metadata",
        "method": "GET",
    },
    GET_UNIT_DATA: {
        "url": "/v1/unit_data",
        "method": "GET",
    },
    GET_SURVEY_LIST: {
        "url": "/v1/survey_list",
        "method": "GET",
    }
}


CIR_ENDPOINTS: dict[str, EndpointConfig] = {
    GET_CI_METADATA: {
        "url": "/collection-instruments/metadata",
        "method": "GET",
    },
    GET_CI_SCHEMA: {
        "url": "/collection-instruments/schema",
        "method": "GET",
    },
    GET_CI_VALIDATOR_METADATA: {
        "url": "/collection-instruments/validator-metadata",
        "method": "GET",
    },
    POST_CI: {
        "url": "/collection-instruments",
        "method": "POST",
    },
    PUT_VALIDATOR_VERSION: {
        "url": "/collection-instruments/validator-version",
        "method": "PUT",
    },
}

SDS_ENDPOINTS_CHOICE: list = ["all"] + list(SDS_ENDPOINTS.keys())
CIR_ENDPOINTS_CHOICE: list = ["all"] + list(CIR_ENDPOINTS.keys())