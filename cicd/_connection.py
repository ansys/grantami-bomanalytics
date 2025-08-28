from importlib.metadata import version
from typing import Optional

from ansys.grantami.serverapi_openapi.v2025r2 import models
from ansys.openapi.common import SessionConfiguration, ApiClientFactory, generate_user_agent, ApiClient

_SERVICE_PATH = "/proxy/v1.svc/mi"
_MI_AUTH_PATH = "/v1alpha/schema/mi-version"
_GRANTA_APPLICATION_NAME_HEADER = "PyGranta ServerAPI"


class Connection(ApiClientFactory):
    def __init__(self, api_url: str, session_configuration: Optional[SessionConfiguration] = None) -> None:
        package_name = "ansys-grantami-serverapi-openapi"
        ver = version(package_name)

        self._full_api_url = api_url.strip("/") + _SERVICE_PATH
        auth_url = self._full_api_url + _MI_AUTH_PATH

        super().__init__(auth_url, session_configuration)
        session_configuration = self._session_configuration
        session_configuration.headers["X-Granta-ApplicationName"] = _GRANTA_APPLICATION_NAME_HEADER
        session_configuration.headers["User-Agent"] = generate_user_agent(package_name, ver)

    def connect(self) -> ApiClient:
        self._validate_builder()
        client = ApiClient(
            session=self._session,
            api_url=self._full_api_url,
            configuration=self._session_configuration,
        )
        client.setup_client(models)
        return client
