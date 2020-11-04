from enum import IntEnum, unique


@unique
class SupportedLanguage(IntEnum):
    """
    Language supported by the app.
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
            "en": SupportedLanguage.EN,
            "en-us": SupportedLanguage.EN,
            "en-gb": SupportedLanguage.EN
        }

        return languages.get(ietf_tag, SupportedLanguage.EN)
