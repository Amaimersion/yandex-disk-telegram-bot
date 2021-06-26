from enum import Enum, unique

from flask import g, request
from flask_babel import (
    gettext as babel_gettext,
    lazy_gettext as babel_lazy_gettext
)

from src.extensions import babel


@unique
class SupportedLanguage(Enum):
    """
    Language that is supported by the app.
    """
    # values should be same as babel values
    EN = "en"

    @staticmethod
    def get(ietf_tag: str) -> "SupportedLanguage":
        """
        Selects supported language by provided IETF language tag.

        - "EN" will be returned if specified
        language not supported

        :returns:
        Enum instance, not actual string.
        """
        ietf_tag = ietf_tag.lower()
        languages = {
            "en": SupportedLanguage.EN
        }

        return languages.get(ietf_tag, SupportedLanguage.EN)


@babel.localeselector
def get_locale() -> str:
    """
    Selects locale for incoming request that Babel will use.

    - most appropriate language will be selected
    """
    result = None
    have_db_data = (
        # `hasattr` should be used because request
        # can came not only from `webhook` blueprint
        hasattr(g, "db_user") and
        g.db_user and
        g.db_user.settings and
        g.db_user.settings.language
    )

    if have_db_data:
        result = g.db_user.settings.language.value
    elif request.accept_languages:
        result = request.accept_languages.best_match(
            [lang.value for lang in SupportedLanguage]
        )

    if result is None:
        result = SupportedLanguage.EN.value

    return result


def gettext(text: str, **kwargs) -> str:
    """
    Gets translation for provided text.

    Based on GNU gettext. If translation not available,
    then provided text will be used instead. Should be used
    only inside of request (for example, on function call to
    handle request). To use this outside of request, see `lazy_gettext`.

    NOTE:
    to use template strings, you should use old way of substitution.
    For example, `"text %(template)s"`, where `kwargs` contains
    `template="value"`. Other methods are not supported.
    """
    return babel_gettext(text, **kwargs)


def lazy_gettext(text: str, **kwargs) -> str:
    """
    Same as `gettext`, but can be used outside of request.

    From Flask-Babel documentation:
    "Lazy strings will not be evaluated until they are actually used".

    For example, it can be used to define constants on application startup.
    """
    return babel_lazy_gettext(text, **kwargs)
