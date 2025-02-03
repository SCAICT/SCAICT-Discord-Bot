"""
This is the module for the class for language utilities.
"""


class LanguageUtils:
    """
    The LanguageUtils class deals with language utilities.
    """

    @staticmethod
    def get_bcp_47_prefix_mapping() -> dict[str, str]:
        """
        Get the mapping of unnormalized BCP 47 language tag prefix to\
        normalized BCP 47 language tag prefix.

        Returns:
            dict[str, str]: The mapping of unnormalized BCP 47 language tag\
                prefix to normalized BCP 47 language tag prefix.
        """

        return {
            "art-lojban": "jbo",
            "en-GB-oed": "en-GB-oxendict",
            "i-ami": "ami",
            "i-bnn": "bnn",
            "i-hak": "hak",
            "i-klingon": "tlh",
            "i-lux": "lb",
            "i-navajo": "nv",
            "i-pwn": "pwn",
            "i-tao": "tao",
            "i-tay": "tay",
            "i-tsu": "tsu",
            "no-bok": "nb",
            "no-nyn": "nn",
            "sgn-BE-FR": "sfb",
            "sgn-BE-NL": "vgt",
            "sgn-BR": "bzs",
            "sgn-CH-DE": "sgg",
            "sgn-CO": "csn",
            "sgn-DE": "gsg",
            "sgn-DK": "dsl",
            "sgn-ES": "ssp",
            "sgn-FR": "fsl",
            "sgn-GB": "bfi",
            "sgn-GR": "gss",
            "sgn-IE": "isg",
            "sgn-IT": "ise",
            "sgn-JP": "jsl",
            "sgn-MX": "mfs",
            "sgn-NI": "ncs",
            "sgn-NL": "dse",
            "sgn-NO": "nsl",
            "sgn-PT": "psr",
            "sgn-SE": "swl",
            "sgn-US": "ase",
            "sgn-ZA": "sfs",
            "zh-cmn": "cmn",
            "zh-gan": "gan",
            "zh-guoyu": "cmn",
            "zh-hakka": "hak",
            "zh-min-nan": "nan",
            "zh-nan": "nan",
            "zh-wuu": "wuu",
            "zh-xiang": "hsn",
            "zh-yue": "yue",
        }

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
    def get_discord_code_to_bcp_47_mapping(cls, /) -> dict:
        """
        Get the mapping of Discord locale code to BCP 47 language tag.

        Returns:
            dict: The mapping of Discord locale code to BCP 47 language tag.
        """

        return {v: k for k, v in cls.get_discord_code_mapping().items()}

    @staticmethod
    def to_bcp_47_case(tag: str, /) -> str:
        """
        Convert language tag string to BCP 47 letter case.

        * language subtag: all lowercase. For example, zh.
        * script subtag: first letter uppercase. For example, Latn.
        * region subtag: all uppercase. For example, TW.
        * variant subtags: all lowercase. For example, wadegile.

        Parameters:
            tag (str): BCP 47 language tag string.

        Returns:
            str: BCP 47 language tag string with BCP 47 letter case.
        """

        tag_lower_subtags: list[str] = tag.lower().split("-")
        tag_bcp_47_case_subtags: list[str] = []

        for index, subtag in enumerate(tag_lower_subtags):
            if index > 0 and tag_lower_subtags[index - 1] == "x":
                # When the previous segment is x, it is a private subtag and
                # should be lowercase
                tag_bcp_47_case_subtags.append(subtag.lower())
            elif len(subtag) == 2 and index > 0:
                # BCP 47 region subtag
                tag_bcp_47_case_subtags.append(subtag.upper())
            elif len(subtag) == 4 and index > 0:
                # BCP 47 script subtag
                tag_bcp_47_case_subtags.append(subtag.title())
            else:
                # Use lowercase for other cases
                tag_bcp_47_case_subtags.append(subtag.lower())

        return "-".join(tag_bcp_47_case_subtags)

    @classmethod
    def to_bcp_47(cls, tag: str, /) -> str:
        """
        Normalize language tag string to BCP 47 language tag string, with
        letter case formatting and deprecated code replacements (for example,
        zh-min-nan => nan).

        Parameters:
            tag (str): Unnormalized BCP 47 language tag string.

        Returns:
            str: Normalized BCP 47 language tag string.
        """

        tag = tag.lower()

        for k, v in cls.get_bcp_47_prefix_mapping().items():
            if tag.startswith(k):
                tag = v + tag.removeprefix(k)

                break

        return cls.to_bcp_47_case(tag)

    @classmethod
    def is_supported_discord_code(cls, code: str, /) -> bool:
        """
        Check if the given code is a supported Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            bool: Whether the given code is a supported Discord locale code.
        """

        return code in cls.get_supported_discord_codes()

    @classmethod
    def get_discord_code(cls, tag: str, /) -> str | None:
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
    def get_from_discord_code(cls, code: str, /) -> str:
        """
        Get the BCP 47 language tag from Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            str: the BCP 47 language tag of the Discord locale code.
        """

        return cls.get_discord_code_to_bcp_47_mapping().get(code, code)
