# Port Conflict Fix

## Problem
The football-predictor application was experiencing BUILD_ID errors due to port conflicts with the existing "kings" project (https://github.com/knoticoo/kings) which uses port 8001.

## Solution
Updated all port configurations to avoid conflicts:

### Port Changes
| Service | Old Port | New Port | Reason |
|---------|----------|----------|---------|
| Frontend | 3001 | 3002 | Avoid potential conflicts |
| Backend API | 8001 | 8003 | **Conflict with kings project** |
| Telegram Bot | 8002 | 8004 | Avoid potential conflicts |
| Redis | 6379 | 6380 | Avoid potential conflicts |
| Nginx HTTP | 80 | 8080 | Avoid system port conflicts |
| Nginx HTTPS | 443 | 8443 | Avoid system port conflicts |

### Files Modified
- `docker-compose.yml` - Updated port mappings
- `frontend/.env` - Updated API URL
- `frontend/.env.example` - Updated example configuration
- `frontend/lib/api.ts` - Updated default API URL
- `frontend/next.config.js` - Updated API URL configuration
- `scripts/deploy.sh` - Updated health check URLs and service URLs

### New Service URLs
After deployment, services will be available at:
- **Frontend**: http://localhost:3002
- **Backend API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs
- **Telegram Bot**: http://localhost:8004
- **Nginx (HTTP)**: http://localhost:8080
- **Nginx (HTTPS)**: https://localhost:8443

## Testing
1. Stop any existing containers: `docker compose down`
2. Rebuild and start: `docker compose up --build -d`
3. Verify services are accessible at new ports
4. Check logs: `docker compose logs frontend`

## Backward Compatibility
This is a breaking change for existing deployments. Users will need to:
1. Update their bookmarks to use new ports
2. Update any external integrations pointing to old ports
3. Update environment variables if using custom configurations

## Related Issues
- Fixes BUILD_ID error caused by port 8001 conflict with kings project
- Resolves Docker container startup failures
- Prevents future port conflicts with other applications