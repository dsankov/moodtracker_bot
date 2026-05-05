from app.config import settings

LANG = settings.BOT_LANGUAGE

_ru = {
    # --- shared buttons ---
    "btn.ok": "OK",
    "btn.cancel": "Отмена",
    "btn.back": "Назад ↩️",
    # --- mood dialog ---
    "mood.select_header": "Выберите 3 эмоции, которые вы испытываете прямо сейчас",
    "mood.selected_header": "Вы выбрали: {choices} ({count} из {max})",
    "mood.validation_alert": "Выбрано {current}/{max}. Нужно ровно {max} эмоции.",
    "mood.saved_demo": "Запись сохранена! (демо-режим)",
    "mood.emotion_checked": "✅ {item.name}",
    "mood.btn_proceed": "Записать",
    "mood.btn_save": "Записать ✅",
    "mood.confirm_header": "Вы выбрали:\n\n{emotions_list}",
    # --- greeting dialog ---
    "greeting.hello": "Привет, {first_name}! 👋",
    "greeting.welcome_new": "Добро пожаловать в Mood Tracker Bot!",
    "greeting.welcome_desc": (
        "Я помогу вам отслеживать настроение и получать инсайты."
    ),
    "greeting.first_seen": "Мы впервые встретились: {first_seen}",
    "greeting.last_help": "Последний раз вы использовали /help: {last_help}",
    "greeting.unknown_date": "неизвестно",
    "greeting.no_help_yet": "Вы ещё не использовали /help.",
    # --- help dialog ---
    "help.text": (
        "Привет!\n"
        "/start — перезапустить\n"
        "/mood — записать настроение\n"
        "/help — это сообщение\n"
        "/language — сменить язык"
    ),
    # --- bot commands ---
    "cmd.start": "Запустить бота",
    "cmd.mood": "Записать настроение",
    "cmd.help": "Помощь",
    "cmd.language": "Сменить язык",
    # --- language dialog ---
    "language.select": "Выберите язык / Select language:",
    "language.current": "Текущий язык: {lang_name}",
    "language.changed": "✅ Язык изменён на русский!",
    # --- admin notifications ---
    "admin.bot_started": "mood_trackerbot started",
    "admin.bot_stopped": "mood_trackerbot stopped",
}

_en = {
    # --- shared buttons ---
    "btn.ok": "OK",
    "btn.cancel": "Cancel",
    "btn.back": "Back ↩️",
    # --- mood dialog ---
    "mood.select_header": "Choose 3 emotions you are feeling right now",
    "mood.selected_header": "You selected: {choices} ({count} of {max})",
    "mood.validation_alert": (
        "Selected {current}/{max}. Exactly {max} emotions required."
    ),
    "mood.saved_demo": "Entry saved! (demo mode)",
    "mood.emotion_checked": "✅ {item.name}",
    "mood.btn_proceed": "Record",
    "mood.btn_save": "Record ✅",
    "mood.confirm_header": "You selected:\n\n{emotions_list}",
    # --- greeting dialog ---
    "greeting.hello": "Hello, {first_name}! 👋",
    "greeting.welcome_new": "Welcome to Mood Tracker Bot!",
    "greeting.welcome_desc": "I can help you track your mood and provide insights.",
    "greeting.first_seen": "We first met: {first_seen}",
    "greeting.last_help": "Last time you used /help: {last_help}",
    "greeting.unknown_date": "unknown",
    "greeting.no_help_yet": "You haven't used /help yet.",
    # --- help dialog ---
    "help.text": (
        "Hello!\n"
        "/start for restart\n"
        "/mood to track your mood\n"
        "/help for this message\n"
        "/language to change language"
    ),
    # --- bot commands ---
    "cmd.start": "Start bot",
    "cmd.mood": "Record mood",
    "cmd.help": "Help",
    "cmd.language": "Change language",
    # --- language dialog ---
    "language.select": "Choose language / Выберите язык:",
    "language.current": "Current language: {lang_name}",
    "language.changed": "✅ Language changed to English!",
    # --- admin notifications ---
    "admin.bot_started": "mood_trackerbot started",
    "admin.bot_stopped": "mood_trackerbot stopped",
}

_messages = {"ru": _ru, "en": _en}

LANG_NAMES = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """Return localised string, optionally formatted with *kwargs*."""
    lang = lang or LANG
    msg = _messages[lang][key]
    return msg.format(**kwargs) if kwargs else msg
