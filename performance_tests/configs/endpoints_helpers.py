from urllib.parse import quote, urlencode

from locust.clients import ResponseContextManager
from locust.contrib.fasthttp import FastHttpSession, FastResponse

from performance_tests.configs.config import config
from performance_tests.configs.endpoints_config import (
    RUNTIME_DATASET_ID_PLACEHOLDER,
    RUNTIME_SCHEMA_ID_PLACEHOLDER,
    EndpointConfig,
)
from performance_tests.configs.runtime_config import RuntimeConfig
from performance_tests.locust_helper import LocustHelper

locust_helper = LocustHelper()


class EndpointsHelpers:
    def __init__(self, base_url: str, endpoints: dict[str, EndpointConfig]):
        self.base_url = base_url
        self.endpoints = endpoints

    def get_endpoint_url(self, endpoint_name: str) -> str:
        """Get the URL for a given endpoint name"""
        return self.endpoints[endpoint_name]["url"]

    def get_endpoint_method(self, endpoint_name: str) -> str:
        """Get the HTTP method for a given endpoint name"""
        return self.endpoints[endpoint_name]["method"]

    def get_endpoint_params(self, endpoint_name: str) -> dict[str, str] | None:
        """Get the parameters for a given endpoint name"""
        return self.endpoints[endpoint_name].get("params")

    def get_endpoint_group_name(self, endpoint_name: str) -> str | None:
        """Get the group name for a given endpoint name"""
        return self.endpoints[endpoint_name].get("name")

    def get_endpoint_payload(self, endpoint_name: str) -> str | None:
        """Get the payload for a given endpoint name"""
        return self.endpoints[endpoint_name].get("payload")

    def has_query_parameters(self, endpoint_name: str) -> bool:
        """Check if the endpoint has query parameters"""
        return self.endpoints[endpoint_name].get("query_parameters", False)

    def get_endpoint_configs_from_selection(self, selected_endpoints: list[str]) -> dict[str, EndpointConfig]:
        """Get the endpoints config for the selected endpoints"""
        if "all" in selected_endpoints:
            return self.endpoints

        return {endpoint: endpoint_config for endpoint, endpoint_config in self.endpoints.items() if endpoint in selected_endpoints}

    def generate_full_url(self, endpoint_name: str, params: dict[str, str] | None = None) -> str:
        """Generate the URL-encoded parameters for a given endpoint name and parameters"""
        url = self.get_endpoint_url(endpoint_name)
        has_qp = self.has_query_parameters(endpoint_name)

        if params:
            encoded_params = self.encode_params(params)
            url = url.format(**encoded_params)
            if has_qp:
                url += f"?{urlencode(params)}"

        full_url = f"{self.base_url}{url}"

        return full_url

    def map_params_to_runtime_values(self, params: dict[str, str | dict], runtime_config: RuntimeConfig) -> dict[str, str]:
        """Map the parameters for a given endpoint name to their corresponding runtime values"""
        mapped_params = {}

        for key, value in params.items():
            if isinstance(value, dict):
                # Recursively map nested parameters
                mapped_params[key] = self.map_params_to_runtime_values(value, runtime_config)
            elif value == RUNTIME_DATASET_ID_PLACEHOLDER:
                mapped_params[key] = runtime_config.DATASET_ID
            elif value == RUNTIME_SCHEMA_ID_PLACEHOLDER:
                mapped_params[key] = runtime_config.SCHEMA_GUID
            else:
                mapped_params[key] = value

        return mapped_params

    def send_request(self, client: FastHttpSession, endpoint_name: str, runtime_config: RuntimeConfig) -> ResponseContextManager | FastResponse:
        """Send a request to the given URL using the specified HTTP method and headers"""

        # Get the endpoint method
        method = self.get_endpoint_method(endpoint_name)

        # Get the endpoint parameters and generate the full URL
        params = self.get_endpoint_params(endpoint_name)
        if params:
            mapped_params = self.map_params_to_runtime_values(params, runtime_config)
            processed_params = self.generate_params_value_from_endpoints_func(mapped_params)
            full_url = self.generate_full_url(endpoint_name, params=processed_params)
        else:
            full_url = self.generate_full_url(endpoint_name)

        # Get the endpoint group name for stat report
        group_name = self.get_endpoint_group_name(endpoint_name)
        if group_name:
            group_name = f"{config.BASE_URL}{group_name}"

        # Load and map payload if it exists for the endpoint
        payload = self.get_endpoint_payload(endpoint_name)
        if payload:
            payload_json = locust_helper.load_json(payload)
            payload = locust_helper.map_schema_payload(payload_json)

        return client.request(
            method=method,
            url=full_url,
            headers=runtime_config.HEADER,
            name=group_name,
            json=payload
        )

    @staticmethod
    def generate_params_value_from_endpoints_func(params: dict[str, str | dict]) -> dict[str, str]:
        """Get the parameter values by calling the corresponding functions if set"""
        output_params = {}

        for key, value in params.items():
            if isinstance(value, dict):
                v = value.get("value")
                func = value.get("function")

                if not func:
                    output_params[key] = value
                elif not v:
                    output_params[key] = func()
                elif isinstance(v, list):
                    output_params[key] = func(*v)
                else:
                    output_params[key] = func(v)
            else:
                output_params[key] = value

        return output_params

    @staticmethod
    def encode_params(params: dict[str, str]):
        """
        Safely return the params dictionary, or an empty dictionary if None is passed in.

        :param params: dictionary containing the parameters to be used in the URL
        :return: dictionary containing the parameters to be used in the URL
        """
        return {key: quote(str(val)) for key, val in params.items()}
