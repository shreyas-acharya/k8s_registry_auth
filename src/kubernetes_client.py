"""Client to interact with kubernetes."""

import base64
import json
from pathlib import Path

import kubernetes


class KubernetesClient:
    """Kubernetes client."""

    def __init__(self, host: str, token_path: str, ca_cert_path: str) -> None:
        """Initialize KubernetesClient."""
        with Path.open(Path(token_path)) as file:
            token: str = file.read()

        configuration = kubernetes.client.Configuration(
            host=host,
            api_key={"authorization": token},
            api_key_prefix={"authorization": "Bearer"},
        )
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = ca_cert_path
        self.client = kubernetes.client.ApiClient(configuration)

    def __del__(self) -> None:
        """Destructor for KubernetesClient."""
        self.client.close()

    def check_if_secret_exists(self, namespace: str, secret_name: str) -> bool:
        """Check if the secret exists."""
        instance = kubernetes.client.CoreV1Api(self.client)
        continue_token: None | str = None

        while True:
            if continue_token:
                response = instance.list_namespaced_secret(namespace, limit=50)
            else:
                response = instance.list_namespaced_secret(
                    namespace,
                    limit=50,
                    _continue=continue_token,
                )

            for item in response["items"]:
                if item["metadata"]["name"] == secret_name:
                    return True

            if response["metadata"]["remaining_item_count"]:
                continue_token = response["metadata"]["_continue"]
            else:
                break

        return False

    def create_docker_secret(
        self,
        namespace: str,
        secret_name: str,
        docker_configuration: dict,
    ) -> None:
        """Create kubernetes secret containing the docker configuration."""
        instance = kubernetes.client.CoreV1Api(self.client)
        instance.create_namespaced_secret(
            namespace,
            kubernetes.client.V1Secret(
                api_version="v1",
                kind="Secret",
                type="kubernetes.io/dockerconfigjson",
                metadata=kubernetes.client.V1ObjectMeta(
                    name=secret_name,
                    namespace=namespace,
                ),
                data={
                    ".dockerconfigjson": base64.b64encode(
                        json.dumps(docker_configuration).encode("utf-8"),
                    ).decode("utf-8"),
                },
            ),
        )

    def update_docker_secret(
        self,
        namespace: str,
        secret_name: str,
        docker_configuration: dict,
    ) -> None:
        """Update kubernetes secret."""
        instance = kubernetes.client.CoreV1Api(self.client)
        instance.patch_namespaced_secret(
            secret_name,
            namespace,
            kubernetes.client.V1Secret(
                data={
                    ".dockerconfigjson": base64.b64encode(
                        json.dumps(docker_configuration).encode("utf-8"),
                    ).decode("utf-8"),
                },
            ),
        )
