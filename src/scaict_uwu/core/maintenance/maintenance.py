"""
This is the module for the abstract class for all maintenance scripts.
"""

# Local imports
# scaict_uwu.maintenance.parameters
from .parameters import MaintenanceParameters


class Maintenance:
    """
    Abstract class for all maintenance scripts.
    """

    _parameters: MaintenanceParameters
    """
    _parameters (MaintenanceParameters)
    """

    def __init__(self) -> None:
        """
        Default constructor. Child classes should call this *first* if
        implementing their own constructors.
        """
        self._parameters = MaintenanceParameters()
        self.add_default_params()

    def add_description(self, description: str) -> None:
        """
        Set description for maintenance scription.

        Parameters:
            description (str): The description to set.
        """
        self.get_parameters().set_description(description)

    def get_parameters(self) -> MaintenanceParameters:
        """
        Returns:
            MaintenanceParameters
        """
        return self._parameters

    def add_default_params(self) -> None:
        """
        TODO
        """

    def can_execute_without_config(self) -> bool:
        """
        Whether this script can run without config.

        Scripts that need to be able to run before installed should override\
        this to return true.

        Scripts that return true from this method will fail with a fatal error
        if attempt to access the database.

        Subclasses that override this method to return true should also\
        override get_db_type() to return self::DB_NONE.
        """
        return False

    def execute(self) -> bool:
        """
        Do the actual work. All child classes will need to implement this.

        Returns:
            bool: True for success, false for failure.
                Returning false for failure will cause\
                do_maintenance.py to exit the process with a non-zero exit\
                status.

        Raises:
            NotImplementedError: The method must be implemented in subclass.
        """
        # Abstract
        raise NotImplementedError
