"""
Unit test for using Pytest.
"""

# Standard imports
from typing import Callable

# Local imports
from scaict_uwu import service_wiring


def test_get_wiring() -> None:
    service_instantiators = service_wiring.get_wiring()

    for name, instantiator in service_instantiators.items():
        assert isinstance(name, str)
        assert isinstance(instantiator, Callable)
