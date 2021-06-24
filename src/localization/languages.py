from enum import Enum, unique

from flask import g, request

from src.extensions import babel


@unique
class SupportedLanguage(Enum):
    """
    Language supported by the app.
    """
    # values should be same as babel values
    EN = "en"

    @staticmethod
    def get(ietf_tag: str) -> "SupportedLanguage":
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


@babel.localeselector
def get_locale():
    """
    Selects locale for incoming request.
    Most appropriate language will be selected.
    """
    result = None
    have_db_data = (
        g.db_user and
        g.db_user.settings and
        g.db_user.settings.language
    )

    if have_db_data:
        result = g.db_user.settings.language.value
    elif request.accept_languages:
        result = request.accept_languages.best_match([
            SupportedLanguage.EN.value
        ])

    if result is None:
        result = SupportedLanguage.EN.value

    return result
