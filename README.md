# TG Monopoly

Telegram Mini App multiplayer Monopoly game with real-time WebSocket gameplay. Built with Django Channels, React, and Pixi.js.

> **Note**: This is a personal learning project, not actively maintained.

## Features

- Real-time multiplayer gameplay via WebSockets
- Telegram Mini App integration with native authentication
- Classic Monopoly mechanics: property buying, rent, auctions, jail, chance cards
- Animated game board with dice rolls and player movements
- Lobby system for creating and joining games

## Tech Stack

**Backend**
- Django 5.2 with Django REST Framework
- Django Channels for WebSocket support
- Celery + Redis for background tasks
- Telegram Bot API integration

**Frontend**
- React 19 with TypeScript
- Vite build system
- Tailwind CSS for styling
- Zustand for state management
- React Query for server state
- Storybook for component development

## Project Structure

```
├── game/                   # Django app
│   ├── consumers/          # WebSocket handlers
│   ├── services/           # Game logic (Monopoly rules)
│   ├── views/              # REST API endpoints
│   ├── models.py           # Database models
│   └── game_config/        # Board configurations (JSON)
├── frontend/               # React app
│   ├── src/features/       # Feature modules
│   ├── src/pages/          # Page components
│   ├── src/shared/         # Shared components and hooks
│   └── src/entities/       # Types and context providers
├── bot/                    # Telegram bot
└── tgmonopoly/             # Django project settings
```

## Running Locally

### Prerequisites
- Python 3.12+
- Node.js 18+
- Redis

### Backend

```bash
# Install dependencies
uv sync

# Create .env with required variables:
# DEBUG=True
# TG_BOT_TOKEN=your_telegram_bot_token
# CHANNELS_HOST=localhost
# CHANNELS_PORT=6379

# Run migrations
uv run manage.py migrate

# Seed board configurations
uv run manage.py populate_database

# Start the server
uv run daphne -b 0.0.0.0 -p 8000 tgmonopoly.asgi:application

# In another terminal, start Celery worker
uv run celery -A tgmonopoly worker -l info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up
```

## Architecture

The game uses a client-server architecture with real-time state synchronization:

1. **Authentication**: Telegram Mini App WebApp data verification
2. **Game Creation**: REST API for creating/joining games
3. **Real-time Play**: WebSocket connection for game events
4. **Game Logic**: Server-side `ClassicMonopolyService` handles all Monopoly rules
5. **State Sync**: Game state broadcast to all connected players via Redis pub/sub

## License

MIT
