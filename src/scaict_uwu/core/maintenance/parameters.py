"""
Module parameters for class MaintenanceParameters.
"""


class MaintenanceParameters:
    """
    Command line parameter handler for maintenance scripts.
    """

    __description: str
    """
    __description (str): Short description of what the script does.
    """

    def has_description(self) -> bool:
        """
        Check whether the script has description.

        Returns:
            bool
        """
        return self.__description != ""

    def get_description(self) -> str:
        """
        Get the short description of what the script does.

        Returns:
            str: The short description
        """
        return self.__description

    def set_description(self, text: str) -> None:
        """
        Set a short description of what the script does.

        Parameters:
            text (str)
        """
        self.__description = text

    def get_help(self) -> str:
        """
        Get help text.

        Returns:
            str
        """
        output: list = []

        # Description
        if self.has_description():
            output.append("")

        return "".join(output)
