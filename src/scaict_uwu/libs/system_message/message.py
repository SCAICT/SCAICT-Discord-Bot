"""
This is the module for the class for all system messages.
"""

# Local imports
from ..language.language_tag import LanguageTag


class Message:
    """
    The Message class deals with fetching and processing of system messages.
    """

    _use_lang: str | None = None
    """
    _use_lang (str|None): The language tag of the language for the system\
        message to use.
    """

    _in_lang: str | None = None
    """
    _in_lang (str|None): The language tag of the language that the system\
        message actually used.
    """

    def __init__(
        self,
        key: str,
        params: list,
        use_lang: LanguageTag | None,
    ) -> None:
        """
        Set the language tag of the language that the message expected to use.

        Parameters:
            key (str): Message key.
            params (list): Message parameters.
            use_lang: (Language|None): Language to use (None: defaults to\
                current user language).
        """

    def set_lang(self, lang_tag: str) -> None:
        """
        Set the language tag of the language that the message expected to use.

        Parameters:
            lang_tag (str): The language tag of the language that the message\
                expected to use.
        """

        self._use_lang = lang_tag

    def get_lang(self) -> str:
        """
        Get the final language tag of the language that the message used or\
            falls back to.

        Returns:
            str: Description of return value.
        """

        return self._use_lang or self._in_lang or ""
