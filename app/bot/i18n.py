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
        "/help for this message"
    ),
    # --- bot commands ---
    "cmd.start": "Запустить бота",
    "cmd.mood": "Записать настроение",
    "cmd.help": "Помощь",
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
        "/help for this message"
    ),
    # --- bot commands ---
    "cmd.start": "Start bot",
    "cmd.mood": "Record mood",
    "cmd.help": "Help",
    # --- admin notifications ---
    "admin.bot_started": "mood_trackerbot started",
    "admin.bot_stopped": "mood_trackerbot stopped",
}

_messages = {"ru": _ru, "en": _en}


def t(key: str, **kwargs) -> str:
    """Return localised string, optionally formatted with *kwargs*."""
    msg = _messages[LANG][key]
    return msg.format(**kwargs) if kwargs else msg
