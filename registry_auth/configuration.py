"""Pydantic model for the configuration."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def _split_comma_seperated_string(value: str) -> list[str]:
    return [item.strip() for item in value.split(",")]


class Configuration(BaseModel):
    """Configuration class."""

    REGISTRY_IDS: Annotated[
        list[str],
        BeforeValidator(
            _split_comma_seperated_string,
        ),
    ]
    NAMESPACES: Annotated[
        list[str],
        BeforeValidator(
            _split_comma_seperated_string,
        ),
    ]
    K8S_HOST: str
    SECRET_NAME: str
    SA_TOKEN_FILE: str = Field(
        default="/var/run/secrets/kubernetes.io/serviceaccount/token"
    )
    CA_CERT_FILE: str = Field(
        default="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    )
