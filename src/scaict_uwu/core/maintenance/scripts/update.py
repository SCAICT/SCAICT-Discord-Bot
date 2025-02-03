"""
Run all updaters.

This is used when the database schema is modified and we need to apply patches.
"""

# Local imports
# scaict_uwu.maintenance.maintenance
from ..maintenance import Maintenance


class UpdateMaintenance(Maintenance):
    """
    Maintenance script to run database schema updates.
    """

    def __init__(self) -> None:
        super().__init__()
        self.add_description("Database updater.")

    def execute(self) -> bool:
        return True
