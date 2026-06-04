from urllib.parse import urlencode

from locust.clients import ResponseContextManager
from locust.contrib.fasthttp import FastHttpSession, FastResponse

from configs.endpoints_config import EndpointConfig, DATASET_ID_PLACEHOLDER, SCHEMA_ID_PLACEHOLDER
from configs.runtime_config import RuntimeConfig


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

    def get_endpoint_configs_from_selection(self, selected_endpoints: list[str]) -> dict[str, EndpointConfig]:
        """Get the endpoints config for the selected endpoints"""
        if "all" in selected_endpoints:
            return self.endpoints

        return {endpoint: config for endpoint, config in self.endpoints.items() if endpoint in selected_endpoints}

    def generate_full_url(self, endpoint_name: str, params: dict[str, str] | None) -> str:
        """Generate the URL-encoded parameters for a given endpoint name and parameters"""
        url = self.get_endpoint_url(endpoint_name)
        full_url = f"{self.base_url}{url}"

        if params:
            full_url += f"?{urlencode(params)}"

        return full_url

    def map_params_to_runtime_values(self, params: dict[str, str], runtime_config: RuntimeConfig) -> dict[str, str]:
        """Map the parameters for a given endpoint name to their corresponding runtime values"""
        mapped_params = {}
        for key, value in params.items():
            if value == DATASET_ID_PLACEHOLDER:
                mapped_params[key] = runtime_config.DATASET_ID
            elif value == SCHEMA_ID_PLACEHOLDER:
                mapped_params[key] = runtime_config.SCHEMA_GUID
            else:
                mapped_params[key] = value

        return mapped_params

    def send_request(self, client: FastHttpSession, endpoint_name: str, runtime_config: RuntimeConfig) -> ResponseContextManager | FastResponse:
        """Send a request to the given URL using the specified HTTP method and headers"""
        method = self.get_endpoint_method(endpoint_name)
        params = self.get_endpoint_params(endpoint_name)
        mapped_params = self.map_params_to_runtime_values(params, runtime_config) if params else None
        full_url = self.generate_full_url(endpoint_name, params=mapped_params)

        if method == "GET":
            return client.get(full_url, headers=runtime_config.HEADER)
        elif method == "POST":
            return client.post(full_url, headers=runtime_config.HEADER)
        elif method == "PUT":
            return client.put(full_url, headers=runtime_config.HEADER)
        elif method == "DELETE":
            return client.delete(full_url, headers=runtime_config.HEADER)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

