"""
This is the module for the class for language utilities.
"""


class LanguageUtils:
    """
    The LanguageUtils class deals with language utilities.
    """

    @staticmethod
    def get_supported_discord_codes() -> list[str]:
        """
        Get the Discord locale codes supported by Discord.

        See Pycord discord.commands.core valid_locales (not public)
        See <https://discord.com/developers/docs/reference#locales>

        Returns:
            list[str]: The list of Discord locale codes supported by Discord.
        """

        return [
            "bg",
            "cs",
            "da",
            "de",
            "el",
            "en-GB",
            "en-US",
            # 'es-419' was missing from Pycord
            "es-419",
            "es-ES",
            "fi",
            "fr",
            "hi",
            "hr",
            "hu",
            # 'id' was missing from Pycord
            "id",
            "it",
            "ja",
            "ko",
            "lt",
            "nl",
            "no",
            "pl",
            "pt-BR",
            "ro",
            "ru",
            "sv-SE",
            "th",
            "tr",
            "uk",
            "vi",
            "zh-CN",
            "zh-TW",
        ]

    @staticmethod
    def get_discord_code_mapping() -> dict[str, str]:
        """
        Get the mapping of BCP 47 language tag to Discord locale code.

        Returns:
            dict[str, str]: The mapping of BCP 47 language tag to Discord locale code.
        """

        return {
            "en": "en-US",
            "es": "es-ES",
            "nb": "no",
            "sv": "sv-SE",
            "zh-Hans": "zh-CN",
            "zh-Hant": "zh-TW",
        }

    @classmethod
    def get_discord_code_to_bcp_47_mapping(cls) -> dict:
        """
        Get the mapping of Discord locale code to BCP 47 language tag.

        Returns:
            dict: The mapping of Discord locale code to BCP 47 language tag.
        """

        return {v: k for k, v in cls.get_discord_code_mapping().items()}

    @classmethod
    def is_supported_discord_code(cls, code: str) -> bool:
        """
        Check if the given code is a supported Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            bool: Whether the given code is a supported Discord locale code.
        """

        return code in cls.get_supported_discord_codes()

    @classmethod
    def get_discord_code(cls, tag: str) -> str | None:
        """
        Get the Discord locale code from BCP 47 language tag.

        Parameters:
            tag (str): BCP 47 language tag.

        Returns:
            (str | None): the Discord locale code of the BCP 47 language tag.\
                Return None when there's no corresponding supported Discord\
                locale code.
        """

        code = cls.get_discord_code_mapping().get(tag, tag)

        if cls.is_supported_discord_code(code):
            return code

        return None

    @classmethod
    def get_from_discord_code(cls, code: str) -> str:
        """
        Get the BCP 47 language tag from Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            str: the BCP 47 language tag of the Discord locale code.
        """

        return cls.get_discord_code_to_bcp_47_mapping().get(code, code)
