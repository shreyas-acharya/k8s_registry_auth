"""Pydantic model for the configuration."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def _split_comma_seperated_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _split_comma_seperated_dictionary(value: str) -> dict[str, str]:
    items: dict[str, str] = {}
    for item in value.split(","):
        parts: list[str] = item.strip().split(":")
        items[parts[0].strip()] = parts[1].strip()
    return items


class Configuration(BaseModel):
    """Configuration class."""

    REGISTRY_IDS: Annotated[
        list[str],
        BeforeValidator(
            _split_comma_seperated_list,
        ),
    ]
    NAMESPACES: Annotated[
        list[str],
        BeforeValidator(
            _split_comma_seperated_list,
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
    LABELS: Annotated[
        dict[str, str], BeforeValidator(_split_comma_seperated_dictionary)
    ] = Field(default_factory=dict)
    ANNOTATIONS: Annotated[
        dict[str, str], BeforeValidator(_split_comma_seperated_dictionary)
    ] = Field(default_factory=dict)
