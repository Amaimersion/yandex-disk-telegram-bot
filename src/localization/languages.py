from enum import IntEnum, unique


@unique
class SupportedLanguages(IntEnum):
    """
    Languages supported by app.
    """
    EN = 1

    @staticmethod
    def get(ietf_tag: str) -> int:
        """
        Return language by IETF language tag.

        - "EN" will be returned, if specified
        language not supported.
        """
        ietf_tag = ietf_tag.lower()
        languages = {
            "en": SupportedLanguages.EN,
            "en-us": SupportedLanguages.EN,
            "en-gb": SupportedLanguages.EN
        }

        return languages.get(ietf_tag, SupportedLanguages.EN)
