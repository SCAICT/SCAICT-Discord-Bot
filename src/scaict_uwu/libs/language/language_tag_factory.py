"""
This is the module for creating the objects for all languages.
"""

# Standard imports
from typing import ClassVar

# Local imports
from .language_tag import LanguageTag
from .language_utils import LanguageUtils


class LanguageTagFactory:
    """
    The LanguageTagFactory class deals with LanguageTag object creations.
    """

    _tags: ClassVar[dict[str, LanguageTag]] = {}
    """
    _tags (dict): The LanguageTag objects.
    """

    def _get(self, tag: str, /) -> LanguageTag:
        """
        Get LanguageTag object by normalized BCP 47 language tag.

        Parameters:
            tag (str): Normalized BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the corresponding BCP 47\
                language tag.
        """

        if tag not in self._tags:
            self._tags[tag] = LanguageTag(tag)

        return self._tags[tag]

    def get(self, tag: str, /) -> LanguageTag:
        """
        Get LanguageTag object by normalized BCP 47 language tag.

        Parameters:
            tag (str): Normalized BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the corresponding BCP 47\
                language tag.
        """

        tag = LanguageUtils.to_bcp_47_case(tag)

        return self._get(tag)

    def get_by_unnormalized(self, tag: str, /) -> LanguageTag:
        """
        Get LanguageTag object by unnormalized BCP 47 language tag.

        Parameters:
            tag (str): Unnormalized BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the corresponding BCP 47\
                language tag.
        """

        tag = LanguageUtils.to_bcp_47(tag)

        return self._get(tag)

    def get_by_discord_code(self, code: str, /) -> LanguageTag | None:
        """
        Get LanguageTag object by Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            (LanguageTag | None): The LanguageTag object of the corresponding\
                Discord locale code. Return None when is not a supported\
                Discord locale code.
        """

        if code not in LanguageUtils.get_supported_discord_codes():
            return None

        tag = LanguageUtils.get_from_discord_code(code)

        return self._get(tag)
