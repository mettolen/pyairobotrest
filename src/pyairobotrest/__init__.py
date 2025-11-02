"""Python library for Airobot thermostat REST API."""

from importlib.metadata import version

from .client import AirobotClient
from .exceptions import (
    AirobotAuthError,
    AirobotConnectionError,
    AirobotError,
    AirobotTimeoutError,
)
from .models import SettingFlags, StatusFlags, ThermostatSettings, ThermostatStatus

__version__ = version("pyairobotrest")

__all__ = [
    "AirobotClient",
    "AirobotError",
    "AirobotConnectionError",
    "AirobotAuthError",
    "AirobotTimeoutError",
    "ThermostatStatus",
    "StatusFlags",
    "ThermostatSettings",
    "SettingFlags",
]
