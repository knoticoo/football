# Football Predictor Deployment Guide

## Quick Start

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your Telegram bot token and other settings
   ```

2. **Deploy Services**
   ```bash
   ./scripts/deploy.sh
   ```

## What the Deploy Script Does

### ✅ Safe Service Management
- **Only stops Football Predictor services** - won't affect other services on ports 5000, 5001, etc.
- Uses project-specific Docker Compose commands to avoid conflicts
- Checks for port conflicts before starting services

### 🔧 Docker Management
- Automatically installs Docker if not present
- Starts Docker daemon if not running
- Handles Docker group permissions

### 🚀 Service Deployment
- Builds and starts all Football Predictor services
- Performs health checks on all services
- Provides detailed status and management commands

## Services and Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3002 | Next.js web application |
| Backend API | 8003 | FastAPI backend |
| Telegram Bot | 8004 | Bot webhook server |
| Redis | 6380 | Background task queue |
| Nginx | 8080 | Reverse proxy |

## Management Commands

```bash
# View all logs
docker compose --project-name football-predictor logs -f

# View specific service logs
docker compose --project-name football-predictor logs -f backend
docker compose --project-name football-predictor logs -f frontend
docker compose --project-name football-predictor logs -f telegram-bot

# Stop services
docker compose --project-name football-predictor down

# Restart services
docker compose --project-name football-predictor restart

# Check service status
docker compose --project-name football-predictor ps
```

## Environment Configuration

Required environment variables in `.env`:

```bash
# Telegram Bot (Required)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
BOT_USERNAME=CodyTips_Bot
ADMIN_USER_IDS=123456789,987654321

# Database
DATABASE_URL=sqlite:///./football_predictor.db

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## Troubleshooting

### Docker Issues
- If Docker is not installed, the script will install it automatically
- If Docker daemon is not running, the script will start it
- You may need to log out and back in after Docker installation for group permissions

### Port Conflicts
- The script checks for port conflicts before starting
- If conflicts are detected, you'll see warnings with details
- Change ports in `docker-compose.yml` if needed

### Service Health Checks
- All services are health-checked after deployment
- If a service fails, check the logs for details
- Services may take up to 2 minutes to become healthy

## Safety Features

- **Isolated Deployment**: Only manages Football Predictor services
- **Port Conflict Detection**: Warns about potential conflicts
- **Project-Specific Commands**: Uses `--project-name football-predictor` to avoid conflicts
- **Graceful Error Handling**: Provides clear error messages and solutions