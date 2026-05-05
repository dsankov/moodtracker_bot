from app.bot.locales.en import _en
from app.bot.locales.ru import _ru
from app.config import settings

LANG = settings.BOT_LANGUAGE

_messages: dict[str, dict[str, str]] = {"en": _en, "ru": _ru}

LANG_NAMES = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """Return localised string with fallback chain: lang → en → slug from key.

    Optionally formatted with *kwargs*.
    """
    lang = lang or LANG

    # 1. Try requested language
    msg = _messages.get(lang, {}).get(key)
    if msg is not None:
        return msg.format(**kwargs) if kwargs else msg

    # 2. Fallback to English
    msg = _messages.get("en", {}).get(key)
    if msg is not None:
        return msg.format(**kwargs) if kwargs else msg

    # 3. Fallback to slug derived from key (e.g. "emotion.some_name" → "Some Name")
    slug = key.rsplit(".", maxsplit=1)[-1].replace("_", " ").title()
    return slug.format(**kwargs) if kwargs else slug
