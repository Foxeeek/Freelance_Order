# Freelance AI MVP Skeleton

Production-ready MVP scaffold for a multi-platform freelance order aggregator with Telegram approvals.

## Features
- Plugin-based platform architecture (Freelancehunt implemented as MVP placeholder).
- Order normalization into a shared internal model.
- SQLite persistence through SQLAlchemy 2.x with duplicate prevention (`platform + external_id`).
- Rule-based analysis/scoring for difficulty, fit, hours and price estimates.
- Telegram moderation flow with inline **Approve/Reject** buttons.
- APScheduler polling (default every 10 minutes).

## Project structure
```text
freelance_ai/
  app/
    main.py
    config.py
    database.py
  core/
    models.py
    platform_registry.py
    analyzer.py
    scorer.py
    proposal_generator.py
  platforms/
    base.py
    freelancehunt/
      scraper.py
      parser.py
      __init__.py
    __init__.py
  bot/
    telegram_bot.py
    handlers.py
  services/
    order_service.py
    scheduler.py
  requirements.txt
  README.md
  .env.example
```

## Setup
1. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r freelance_ai/requirements.txt
   ```
3. Configure environment:
   ```bash
   cp freelance_ai/.env.example .env
   ```
4. Fill `.env` values (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, etc.).

## Run
```bash
python -m freelance_ai.app.main
```

## How plugin extension works
1. Create a new folder under `freelance_ai/platforms/<platform_name>/`.
2. Implement class inheriting `BasePlatform` with:
   - `platform_name`
   - `async fetch_orders() -> list[dict]`
   - `parse(raw: dict) -> OrderIn`
3. Register platform in `core/platform_registry.py`.
4. Add platform name to `ENABLED_PLATFORMS` in `.env`.

## Notes for MVP
- Freelancehunt scraper is intentionally fail-safe and returns an empty list on errors.
- Telegram is optional for startup; if token/chat are missing, scheduler still runs.
- Proposal generation is rule-based placeholder (EN default, UA optional).
