from enum import Enum, unique

from flask import (
    g,
    request,
    has_app_context,
    has_request_context
)
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
    RU = "ru"

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
            # All not specified countries
            "en": SupportedLanguage.EN,

            # Russia
            "ru": SupportedLanguage.RU,
            "ru-ru": SupportedLanguage.RU,

            # Ukraine
            "uk": SupportedLanguage.RU,
            "uk-ua": SupportedLanguage.RU,

            # Belarus
            "be": SupportedLanguage.RU,
            "be-by": SupportedLanguage.RU
        }

        return languages.get(ietf_tag, SupportedLanguage.EN)

    def to_native_name(self) -> str:
        """
        :returns:
        Lowercased language name in native language.
        For example, `EN` instance will return `english`.
        """
        code_to_name = {
            SupportedLanguage.EN: "english",
            SupportedLanguage.RU: "русский"
        }

        return code_to_name.get(self)


@babel.localeselector
def localeselector() -> str:
    """
    Selects locale for incoming request that Babel will use.

    - most appropriate language will be selected
    """
    # default locale is EN
    result = SupportedLanguage.EN.value

    # in some places, for example in background tasks,
    # app context (`g`, etc.) not always available, thus
    # usage of missing app context will produce error
    have_app_context = has_app_context()

    # same as `have_app_context`, but for request context
    have_request_context = has_request_context()

    # selection of locale depends on specific DB data,
    # which not always exists, because request can came
    # not only from Telegram `webhook` blueprint, but
    # also from different places which not provide DB data
    have_db_data = (
        hasattr(g, "db_user") and
        g.db_user and
        g.db_user.settings and
        g.db_user.settings.language
    )

    if have_app_context:
        if have_db_data:
            result = g.db_user.settings.language.value
        elif have_request_context:
            if request.accept_languages:
                result = request.accept_languages.best_match(
                    [lang.value for lang in SupportedLanguage]
                )

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
