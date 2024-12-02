"""
This is the module for the class for all languages.
"""

from .language_utils import LanguageUtils


class LanguageTag:
    """
    The LanguageTag class deals with language data.

    Note:
        This class is designed to be instantiated through LanguageTagFactory\
        rather than directly.

        Example:
            language_tag_factory = LanguageTagFactory()
            tag = language_tag_factory.get("zh-Hant")
            tag = language_tag_factory.get_by_discord_code("zh-TW")
    """

    _tag: str
    """
    _tag (str): The BCP 47 language subtag of the LanguageTag object.
    """

    def __init__(self, tag: str) -> None:
        """
        Parameters:
            tag (str): BCP 47 language tag.
        """

        self._tag = tag

    def get_bcp_47_tag(self) -> str:
        """
        Get the BCP 47 language tag of the LanguageTag object.

        Returns:
            str: The BCP 47 language tag.
        """

        return self._tag

    def get_system_message_tag(self) -> str:
        """
        Get the system message language tag of the LanguageTag object.

        Returns:
            str: The system message language tag.
        """

        return self._tag.lower()

    def get_discord_code(self) -> str | None:
        """
        Get the Discord locale code of the LanguageTag object.

        See <https://discord.com/developers/docs/reference#locales>

        Returns:
            (str | None): The Discord locale code. Return None when there is no\
                corresponding supported Discord locale code.
        """

        return LanguageUtils.get_discord_code(self._tag)

    def get_fallbacks(self) -> list[str]:
        """
        Get the language fallback chain of the LanguageTag object.

        Returns:
            list[str]: The list containing BCP 47 language tags of the language\
                fallback chain.
        """

        return []
