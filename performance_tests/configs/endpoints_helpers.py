from urllib.parse import urlencode

from locust.clients import ResponseContextManager
from locust.contrib.fasthttp import FastHttpSession, FastResponse

from configs.endpoints_config import EndpointConfig


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

    def generate_full_url(self, endpoint_name: str, params: dict[str, str] | None) -> str:
        """Generate the URL-encoded parameters for a given endpoint name and parameters"""
        url = self.get_endpoint_url(endpoint_name)
        full_url = f"{self.base_url}{url}"

        if params:
            full_url += f"?{urlencode(params)}"

        return full_url

    def send_request(self, client: FastHttpSession, endpoint_name: str, params: dict[str, str], headers: dict[str, str]) -> ResponseContextManager | FastResponse:
        """Send a request to the given URL using the specified HTTP method and headers"""
        method = self.get_endpoint_method(endpoint_name)
        full_url = self.generate_full_url(endpoint_name, params=params)

        if method == "GET":
            return client.get(full_url, headers=headers)
        elif method == "POST":
            return client.post(full_url, headers=headers)
        elif method == "PUT":
            return client.put(full_url, headers=headers)
        elif method == "DELETE":
            return client.delete(full_url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

