"""
Config
"""

# Standard imports
import sys
from typing import ClassVar


class Config:
    options: ClassVar[dict]

    def get_option(self, name: str):
        if name in self.options:
            return self.options[name]

        sys.exit("NoSuchOptionExpection")
