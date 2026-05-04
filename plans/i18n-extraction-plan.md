# i18n Extraction Plan — Hardcoded Messages → Localisation-Ready Structure

## Goal

Extract every hardcoded user-facing string into a single `app/bot/i18n.py` module with a language-keyed dictionary, so switching to another language requires only adding a new language dict and changing one config value.

---

## Audit — All Hardcoded Strings Found

### [`mood_dialog.py`](app/bot/user/mood_dialog.py)

| Line | Current String | Proposed Key |
|------|---------------|--------------|
| 64 | `"Выберите 3 эмоции, которые вы испытываете прямо сейчас"` | `mood.select_header` |
| 67 | `f"Вы выбрали: {choices_text} ({selected_count} из {MAX_EMOTIONS})"` | `mood.selected_header` |
| 112–113 | `f"Выбрано {len(ordered)}/{MAX_EMOTIONS}. Нужно ровно {MAX_EMOTIONS} эмоции."` | `mood.validation_alert` |
| 130 | `"Запись сохранена! (демо-режим)"` | `mood.saved_demo` |
| 159 | `Format("✅ {item.name}")` | `mood.emotion_checked` |
| 172 | `Const("Записать")` | `mood.btn_proceed` |
| 177 | `Const("Отмена")` | `btn.cancel` |
| 187 | `Format("Вы выбрали:\n\n{emotions_list}")` | `mood.confirm_header` |
| 190 | `Const("Записать ✅")` | `mood.btn_save` |
| 195 | `Const("Назад ↩️")` | `btn.back` |

### [`greeting_dialog.py`](app/bot/user/greeting_dialog.py)

| Line | Current String | Proposed Key |
|------|---------------|--------------|
| 38 | `"unknown"` | `greeting.unknown_date` |
| 39 | `"You haven't used /help yet."` | `greeting.no_help_yet` |
| 71 | `Format("Hello, {first_name}! 👋")` | `greeting.hello` |
| 72 | `Const("Welcome to Mood Tracker Bot!")` | `greeting.welcome_new` |
| 73 | `Const("I can help you track your mood and provide insights.")` | `greeting.welcome_desc` |
| 76 | `Const("OK")` | `btn.ok` |
| 83 | `Format("Hello, {first_name}! 👋")` | `greeting.hello` (reused) |
| 84 | `Format("We first met: {first_seen}")` | `greeting.first_seen` |
| 85 | `Format("Last time you used /help: {last_help}")` | `greeting.last_help` |
| 88 | `Const("OK")` | `btn.ok` (reused) |

### [`help_dialog.py`](app/bot/user/help_dialog.py)

| Line | Current String | Proposed Key |
|------|---------------|--------------|
| 23–27 | `"Hello!\n/start for restart\n/mood to track your mood\n/help for this message"` | `help.text` |
| 29 | `Const("OK")` | `btn.ok` (reused) |

### [`bot_factory.py`](app/bot/bot_factory.py)

| Line | Current String | Proposed Key |
|------|---------------|--------------|
| 29 | `"Запустить бота"` | `cmd.start` |
| 30 | `"Записать настроение"` | `cmd.mood` |
| 31 | `"Помощь"` | `cmd.help` |
| 48 | `"mood_trackerbot started"` | `admin.bot_started` |
| 55 | `"mood_trackerbot stopped"` | `admin.bot_stopped` |

---

## Architecture

### New file: `app/bot/i18n.py`

```
app/bot/i18n.py          ← single source of truth for all strings
app/config.py             ← add BOT_LANGUAGE setting
```

### Module design

```python
# app/bot/i18n.py
from app.config import settings

LANG = settings.BOT_LANGUAGE  # "ru" | "en" | ...

_ru = {
    # --- buttons ---
    "btn.ok":      "OK",
    "btn.cancel":  "Отмена",
    "btn.back":    "Назад ↩️",

    # --- mood dialog ---
    "mood.select_header":    "Выберите 3 эмоции, которые вы испытываете прямо сейчас",
    "mood.selected_header":  "Вы выбрали: {choices} ({count} из {max})",
    "mood.validation_alert": "Выбрано {current}/{max}. Нужно ровно {max} эмоции.",
    "mood.saved_demo":       "Запись сохранена! (демо-режим)",
    "mood.emotion_checked":  "✅ {item.name}",
    "mood.btn_proceed":      "Записать",
    "mood.btn_save":         "Записать ✅",
    "mood.confirm_header":   "Вы выбрали:\n\n{emotions_list}",

    # --- greeting dialog ---
    "greeting.hello":        "Hello, {first_name}! 👋",
    "greeting.welcome_new":  "Welcome to Mood Tracker Bot!",
    "greeting.welcome_desc": "I can help you track your mood and provide insights.",
    "greeting.first_seen":   "We first met: {first_seen}",
    "greeting.last_help":    "Last time you used /help: {last_help}",
    "greeting.unknown_date": "unknown",
    "greeting.no_help_yet":  "You haven't used /help yet.",

    # --- help dialog ---
    "help.text": "Hello!\n/start for restart\n/mood to track your mood\n/help for this message",

    # --- bot commands ---
    "cmd.start": "Запустить бота",
    "cmd.mood":  "Записать настроение",
    "cmd.help":  "Помощь",

    # --- admin notifications ---
    "admin.bot_started": "mood_trackerbot started",
    "admin.bot_stopped": "mood_trackerbot stopped",
}

_en = {
    "btn.ok":      "OK",
    "btn.cancel":  "Cancel",
    "btn.back":    "Back ↩️",

    "mood.select_header":    "Choose 3 emotions you are feeling right now",
    "mood.selected_header":  "You selected: {choices} ({count} of {max})",
    "mood.validation_alert": "Selected {current}/{max}. Exactly {max} emotions required.",
    "mood.saved_demo":       "Entry saved! (demo mode)",
    "mood.emotion_checked":  "✅ {item.name}",
    "mood.btn_proceed":      "Record",
    "mood.btn_save":         "Record ✅",
    "mood.confirm_header":   "You selected:\n\n{emotions_list}",

    "greeting.hello":        "Hello, {first_name}! 👋",
    "greeting.welcome_new":  "Welcome to Mood Tracker Bot!",
    "greeting.welcome_desc": "I can help you track your mood and provide insights.",
    "greeting.first_seen":   "We first met: {first_seen}",
    "greeting.last_help":    "Last time you used /help: {last_help}",
    "greeting.unknown_date": "unknown",
    "greeting.no_help_yet":  "You haven't used /help yet.",

    "help.text": "Hello!\n/start for restart\n/mood to track your mood\n/help for this message",

    "cmd.start": "Start bot",
    "cmd.mood":  "Record mood",
    "cmd.help":  "Help",

    "admin.bot_started": "mood_trackerbot started",
    "admin.bot_stopped": "mood_trackerbot stopped",
}

_messages = {"ru": _ru, "en": _en}


def t(key: str, **kwargs) -> str:
    """Return localised string, optionally formatted with kwargs."""
    msg = _messages[LANG][key]
    return msg.format(**kwargs) if kwargs else msg
```

### Config change: `app/config.py`

Add one field to `Settings`:

```python
BOT_LANGUAGE: str = "ru"
```

### Usage pattern in dialog files

**Before:**
```python
Button(Const("Записать"), id="proceed_btn", on_click=on_proceed_clicked)
```

**After:**
```python
from app.bot.i18n import t
Button(Const(t("mood.btn_proceed")), id="proceed_btn", on_click=on_proceed_clicked)
```

**Before (Format widget):**
```python
Format("Hello, {first_name}! 👋")
```

**After:**
```python
Format(t("greeting.hello"))  # t() returns "Hello, {first_name}! 👋" — Format still does the interpolation
```

**Before (dynamic f-string in getter):**
```python
header = f"Вы выбрали: {choices_text} ({selected_count} из {MAX_EMOTIONS})"
```

**After:**
```python
header = t("mood.selected_header", choices=choices_text, count=selected_count, max=MAX_EMOTIONS)
```

---

## Key Naming Convention

- Dot-separated hierarchy: `<feature>.<element>`
- Shared buttons under `btn.*`
- Feature-specific strings under `<feature>.*`
- Admin/system strings under `admin.*` / `cmd.*`

---

## Files Modified

| File | Change |
|------|--------|
| `app/bot/i18n.py` | **NEW** — all strings, `t()` helper, both `ru` and `en` dicts |
| `app/config.py` | Add `BOT_LANGUAGE: str = "ru"` |
| `app/bot/user/mood_dialog.py` | Replace 10 hardcoded strings with `t()` calls |
| `app/bot/user/greeting_dialog.py` | Replace 7 unique hardcoded strings with `t()` calls |
| `app/bot/user/help_dialog.py` | Replace 2 hardcoded strings with `t()` calls |
| `app/bot/bot_factory.py` | Replace 5 hardcoded strings with `t()` calls |

---

## How to Switch Language

1. Set `BOT_LANGUAGE=en` in `.env`
2. Restart the bot
3. All user-facing text switches to English

To add a new language (e.g. `de`):
1. Add a `_de` dict in `app/bot/i18n.py` with all keys translated
2. Register it: `_messages["de"] = _de`
3. Set `BOT_LANGUAGE=de` in `.env`

---

## Out of Scope

- Per-user language preference (requires DB schema change)
- Runtime language switching without restart
- Log messages (not user-facing)
- Error messages in `app/config.py` and `app/main.py` (developer-facing only)
