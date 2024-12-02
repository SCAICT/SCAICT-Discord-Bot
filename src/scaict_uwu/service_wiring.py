"""
Module for SCAICT-uwu default service implementations.
"""

# Standard imports
from typing import Callable

# Local imports
from .core.config.config import Config
from .core.config.config_factory import ConfigFactory
from .libs.language.language_tag_factory import LanguageTagFactory
from .service_container import ServiceContainer


def get_wiring() -> dict[str, Callable]:
    """
    Get the service instantiator functions.

    Returns:
        dict: A mapping of service names to their instantiator functions.
            Format: {"service_name": instantiator_function}
    """

    return {
        "Config": get_config,
        "ConfigFactory": get_config_factory,
        "LanguageTagFactory": get_language_tag_factory,
    }


def get_config(services: ServiceContainer) -> Config:
    return services.get_config_factory().get()


def get_config_factory(services: ServiceContainer) -> ConfigFactory:
    return ConfigFactory()


def get_language_tag_factory(services: ServiceContainer) -> LanguageTagFactory:
    return LanguageTagFactory()
