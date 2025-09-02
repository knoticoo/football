# Football Prediction Web App with Telegram Bot

A comprehensive football prediction system with web interface and Telegram bot integration.

## Project Structure

```
football-predictor/
├── backend/          # FastAPI backend (Port 8001)
├── frontend/         # React/Next.js frontend (Port 3001)
├── telegram-bot/     # Telegram bot service
├── shared/           # Shared utilities and models
├── docker/           # Docker configurations
├── scripts/          # Deployment and utility scripts
└── docs/            # Documentation
```

## Port Configuration (to avoid conflicts)

- **Backend API**: 8001
- **Frontend**: 3001
- **Telegram Bot**: Webhook on 8002
- **Database**: SQLite (no port conflicts)

## Quick Start

1. **Backend**: `cd backend && pip install -r requirements.txt && uvicorn main:app --port 8001`
2. **Frontend**: `cd frontend && npm install && npm run dev -- --port 3001`
3. **Bot**: `cd telegram-bot && pip install -r requirements.txt && python bot.py`

## Environment Variables

Create `.env` files in each service directory with appropriate configurations.

## Deployment

Use the provided Docker setup for easy deployment on your VPS.