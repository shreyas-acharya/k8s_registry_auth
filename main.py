"""Application to generate the docker configuration file."""

import os
from pathlib import Path

import boto3
import kubernetes

from configuration import Configuration


def _generate_docker_configuration(registry_ids: list[str]) -> dict:
    docker_configuration: dict = {"auths": {}}
    ecr_client = boto3.client("ecr")
    response = ecr_client.get_authorization_token(registryIds=registry_ids)
    for authorization_data in response["authorizationData"]:
        docker_configuration[authorization_data["proxyEndpoint"]] = {
            "auth": authorization_data["authorizationToken"],
        }
    return docker_configuration


def _create_kubernetes_secrets(token_path: str, ca_cert_path: str) -> None:
    with Path.open(Path(token_path)) as file:
        token: str = file.read()

    configuration = kubernetes.client.Configuration(
        api_key=token, api_key_prefix="Bearer"
    )
    configuration.verify_ssl = True
    configuration.ssl_ca_cert = ca_cert_path

    with kubernetes.client.ApiClient(configuration) as api_client:
        api: kubernetes.client.CoreV1Api = kubernetes.client.CoreV1Api(
            api_client,
        )

        print(api.list_namespace())


def main() -> None:
    """Entrypoint for the application."""
    configuration: Configuration = Configuration.model_validate(
        dict(os.environ.items()),
    )
    docker_configuration: dict = _generate_docker_configuration(
        configuration.REGISTRY_IDS
    )


if __name__ == "__main__":
    main()
