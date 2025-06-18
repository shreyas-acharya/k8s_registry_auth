"""Application to generate the docker configuration file."""

import logging
import os

from registry_auth.configuration import Configuration
from registry_auth.docker_client import generate_docker_configuration
from registry_auth.kubernetes_client import KubernetesClient

logger = logging.getLogger(__name__)


def main() -> None:
    """Entrypoint for the application."""
    configuration: Configuration = Configuration.model_validate(
        dict(os.environ.items()),
    )
    logging.basicConfig(level=getattr(logging, configuration.LOG_LEVEL))
    kubernetes_client: KubernetesClient = KubernetesClient(
        configuration.K8S_HOST,
        configuration.SA_TOKEN_FILE,
        configuration.CA_CERT_FILE,
    )

    docker_configuration: dict = generate_docker_configuration(
        ["aws"],
        configuration,
    )
    logger.info(
        "Creating docker configuration secret (%s) in the namespaces : %s",
        configuration.SECRET_NAME,
        ", ".join(configuration.NAMESPACES),
    )
    for namespace in configuration.NAMESPACES:
        if kubernetes_client.check_if_secret_exists(
            namespace,
            configuration.SECRET_NAME,
        ):
            kubernetes_client.update_docker_secret(
                namespace,
                configuration.SECRET_NAME,
                configuration.LABELS,
                configuration.ANNOTATIONS,
                docker_configuration,
            )
        else:
            kubernetes_client.create_docker_secret(
                namespace,
                configuration.SECRET_NAME,
                configuration.LABELS,
                configuration.ANNOTATIONS,
                docker_configuration,
            )


if __name__ == "__main__":
    main()
