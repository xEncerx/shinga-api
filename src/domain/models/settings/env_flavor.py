from enum import Enum


class EnvFlavor(str, Enum):
    """Enumeration for different environment flavors."""

    DEVELOPMENT = "dev"
    STAGING = "stage"
    PRODUCTION = "prod"
