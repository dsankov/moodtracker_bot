# MoodTracker Bot

MoodTracker Bot is a simple and efficient bot designed to help you track your mood over time. This bot allows you to log your daily mood and provides insights into your emotional well-being.

## Features

- Log daily mood entries by selecting emotions from a curated list of 74 emotions
- Emotions organized in 7 logical groups (Fear/Anxiety, Anger/Disgust, Positive/Empowered, Sadness/Shame, Stress/Fatigue, Surprise/Confusion, Gratitude/Contentment)
- Multi-language support (English/Russian) with per-user language preference
- Extensible i18n system — adding new languages requires only a new locale file, no database changes
- Webhook-based Telegram bot with FastAPI backend
- Docker deployment with development (ngrok) and production (nginx) modes

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [uv](https://docs.astral.sh/uv/) (for local development only)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/dsankov/moodtracker_bot.git
    ```
2. Navigate to the project directory:
    ```bash
    cd moodtracker_bot
    ```
3. Copy the environment template and fill in your values:
    ```bash
    cp .env.example .env
    ```

## Usage

### Development (with ngrok)

Start all services (app + PostgreSQL + ngrok):
```bash
make up-all
```

View logs:
```bash
make logs
```

Stop all services:
```bash
make down-all
```

### Production (with nginx on host)

```bash
make prod-up
```

### Local development (without Docker)

Install dependencies and run directly:
```bash
uv sync
uv run python -m app.main
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainer at Dmitry.Sankov@gmail.com.
