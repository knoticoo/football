# Football Prediction Web App with Telegram Bot

A comprehensive football prediction system with web interface and Telegram bot integration.

## 🤖 Telegram Bot

- **Bot Username**: @CodyTips_Bot
- **Bot ID**: 8446527732
- **Bot Name**: DailyTips

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Deploy with one command:**
   ```bash
   ./scripts/deploy.sh
   ```

3. **Access services:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs
   - Telegram Bot: @CodyTips_Bot

### Manual Setup

1. **Backend**: `cd backend && pip install -r requirements.txt && uvicorn main:app --port 8001`
2. **Frontend**: `cd frontend && npm install && npm run dev -- --port 3001`
3. **Bot**: `cd telegram-bot && pip install -r requirements.txt && python main.py`

## 📁 Project Structure

```
football-predictor/
├── backend/          # FastAPI backend (Port 8001)
├── frontend/         # Next.js frontend (Port 3001)
├── telegram-bot/     # Telegram bot service (Port 8002)
├── nginx/            # Nginx reverse proxy
├── scripts/          # Deployment and utility scripts
├── docker-compose.yml
├── .env              # Environment configuration
└── TROUBLESHOOTING.md
```

## 🔧 Port Configuration

- **Backend API**: 8001
- **Frontend**: 3001
- **Telegram Bot**: 8002
- **Redis**: 6379
- **Nginx**: 80, 443

## 📋 Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `SECRET_KEY`: Secret key for JWT tokens

Optional:
- `FOOTBALL_DATA_API_KEY`: API key for football data
- `API_SPORTS_KEY`: API key for sports data
- `ADMIN_USER_IDS`: Comma-separated admin user IDs

## 🛠️ Useful Commands

```bash
# View all logs
docker compose logs -f

# Restart specific service
docker compose restart telegram-bot

# Check service health
./scripts/check-services.sh

# Test bot configuration
./scripts/test-bot.py

# Complete reset
docker compose down -v && docker compose up --build -d
```

## 🆘 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.