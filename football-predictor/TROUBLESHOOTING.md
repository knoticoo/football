# Football Predictor - Troubleshooting Guide

## Common Issues and Solutions

### 1. Health Check Failures

If you see health check failures during startup:

```bash
[WARNING] ⚠️ Backend health check failed
[WARNING] ⚠️ Frontend health check failed
[WARNING] ⚠️ Telegram bot health check failed
```

#### Solutions:

1. **Check container logs:**
   ```bash
   docker compose logs backend
   docker compose logs frontend
   docker compose logs telegram-bot
   ```

2. **Verify environment variables:**
   - Copy `.env.example` to `.env`
   - Set `TELEGRAM_BOT_TOKEN` to a valid token
   - Update other configuration as needed

3. **Check service dependencies:**
   - Backend depends on database initialization
   - Frontend depends on backend being ready
   - Telegram bot depends on backend being ready

### 2. Container Restart Loops

If containers keep restarting:

1. **Check for missing dependencies:**
   ```bash
   docker compose logs backend | grep -i error
   docker compose logs frontend | grep -i error
   docker compose logs telegram-bot | grep -i error
   ```

2. **Verify build process:**
   ```bash
   docker compose build --no-cache
   ```

3. **Check port conflicts:**
   - Ensure ports 3001, 8001, 8002, 6379 are not in use
   ```bash
   netstat -tulpn | grep -E ':(3001|8001|8002|6379)'
   ```

### 3. Database Issues

If you see database-related errors:

1. **Reset database volumes:**
   ```bash
   docker compose down -v
   docker compose up -d
   ```

2. **Check database file permissions:**
   ```bash
   docker compose exec backend ls -la /app/data/
   ```

### 4. Telegram Bot Issues

If the telegram bot fails to start:

1. **Verify bot token:**
   - Ensure `TELEGRAM_BOT_TOKEN` is set correctly
   - Token should be obtained from @BotFather

2. **Check webhook configuration:**
   - If using webhooks, ensure `TELEGRAM_WEBHOOK_URL` is set
   - For local development, leave webhook URL empty for polling mode

### 5. Frontend Build Issues

If frontend fails to build:

1. **Check Node.js dependencies:**
   ```bash
   docker compose exec frontend npm list
   ```

2. **Clear node_modules:**
   ```bash
   docker compose exec frontend rm -rf node_modules
   docker compose exec frontend npm install
   ```

### 6. Network Issues

If services can't communicate:

1. **Check Docker network:**
   ```bash
   docker network ls
   docker network inspect football-predictor_football-predictor
   ```

2. **Verify service names:**
   - Services should use container names for internal communication
   - Backend: `http://backend:8001`
   - Frontend: `http://frontend:3001`

## Health Check Endpoints

- **Backend:** `http://localhost:8001/health`
- **Frontend:** `http://localhost:3001`
- **Telegram Bot:** `http://localhost:8002/health`

## Useful Commands

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f telegram-bot

# Restart specific service
docker compose restart backend

# Rebuild and restart
docker compose up --build -d

# Complete reset
docker compose down -v
docker compose up --build -d

# Check service health
./scripts/check-services.sh
```

## Environment Variables

Required environment variables:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `SECRET_KEY`: Secret key for JWT tokens (change in production)
- `DATABASE_URL`: Database connection string

Optional environment variables:

- `FOOTBALL_DATA_API_KEY`: API key for football data
- `API_SPORTS_KEY`: API key for sports data
- `TELEGRAM_WEBHOOK_URL`: Webhook URL for production
- `ADMIN_USER_IDS`: Comma-separated list of admin user IDs

## Getting Help

If you continue to experience issues:

1. Check the logs for specific error messages
2. Verify all environment variables are set correctly
3. Ensure all required ports are available
4. Try rebuilding containers with `--no-cache` flag