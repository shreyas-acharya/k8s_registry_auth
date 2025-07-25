"""Client to generate the docker configuration."""

import logging

import boto3

from registry_auth.configuration import Configuration

logger = logging.getLogger(__name__)


def _generate_ecr_docker_configuration(
    registry_ids: list[str],
    docker_configuration: dict,
) -> dict:
    logger.debug("Generating docker configuration for ECR ...")
    ecr_client = boto3.client("ecr")
    response = ecr_client.get_authorization_token(registryIds=registry_ids)
    for authorization_data in response["authorizationData"]:
        docker_configuration["auths"][authorization_data["proxyEndpoint"]] = {
            "auth": authorization_data["authorizationToken"],
        }
    return docker_configuration


def generate_docker_configuration(
    platforms: list[str],
    configuration: Configuration,
) -> dict:
    """Generate docker configuration."""
    logger.info(
        "Generating docker configuration for the platforms : %s",
        ", ".join(platforms),
    )
    docker_configuration: dict = {"auths": {}}

    for platform in platforms:
        match platform:
            case "aws":
                _generate_ecr_docker_configuration(
                    configuration.REGISTRY_IDS,
                    docker_configuration,
                )
    return docker_configuration
