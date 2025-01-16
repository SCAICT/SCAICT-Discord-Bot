"""
Config factory
"""

# Local imports
from .config import Config


class ConfigFactory:
    def get(self) -> Config:
        return Config()
