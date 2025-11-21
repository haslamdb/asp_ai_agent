# Rate Limiting Implementation Guide

## Overview

Rate limiting has been implemented to protect against:
- **Brute force attacks** on login endpoints
- **API abuse** and credit draining on LLM endpoints
- **Spam** account creation
- **DoS attacks** through excessive requests

---

## Rate Limits Applied

### 🔐 Authentication Endpoints

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `/login` (POST) | 5 per minute | Prevent brute force password attacks |
| `/signup` (POST) | 3 per hour | Prevent spam registrations |
| `/resend-verification` (POST) | 3 per hour | Prevent email spam |
| `/admin/*` (POST/DELETE) | 5-10 per hour | Prevent admin abuse |

### 🤖 LLM API Endpoints

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `/api/chat` | 30 per minute | General API usage limit |
| `/api/asp-feedback` | 20 per minute | Expensive LLM calls |
| `/api/feedback/enhanced` | 15 per minute | Very expensive (Claude/Gemini + RAG) |
| `/api/modules/cicu/feedback` | 15 per minute | Expensive LLM + RAG calls |

### 🌐 Global Limits

- **Default:** 200 requests per day, 50 per hour (per IP)
- **Method:** Fixed-window strategy
- **Storage:** Memory (upgrade to Redis for production scaling)

---

## How It Works

### Client Identification

Rate limits are applied per IP address using Flask-Limiter's `get_remote_address` function:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Identifies clients by IP
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)
```

### Response When Limit Exceeded

When a client exceeds the rate limit:
- **HTTP Status:** 429 Too Many Requests
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets
- **Response Body:**
  ```json
  {
    "error": "ratelimit exceeded",
    "message": "5 per 1 minute"
  }
  ```

---

## Production Considerations

### Upgrade to Redis

For production with multiple servers, upgrade from memory to Redis storage:

```python
# In unified_server.py, change:
storage_uri="redis://localhost:6379"
```

**Install Redis:**
```bash
sudo apt-get install redis-server
pip install redis
```

### Behind Reverse Proxy (Nginx)

If using Nginx, ensure it forwards the real client IP:

```nginx
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

Then update Flask-Limiter to use forwarded IP:

```python
from flask_limiter.util import get_ipaddr

limiter = Limiter(
    app=app,
    key_func=get_ipaddr,  # Uses X-Forwarded-For header
    ...
)
```

### Whitelist Trusted IPs

To exempt certain IPs (e.g., internal monitoring):

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    exempt_when=lambda: request.remote_addr in ['127.0.0.1', '10.0.0.1']
)
```

---

## Customizing Rate Limits

### Adding Rate Limit to New Endpoint

```python
@app.route('/api/new-endpoint', methods=['POST'])
@limiter.limit("10 per minute")
def new_endpoint():
    return jsonify({'message': 'Success'})
```

### Multiple Limits

Apply both per-minute and per-hour limits:

```python
@app.route('/api/endpoint', methods=['POST'])
@limiter.limit("30 per minute")
@limiter.limit("500 per hour")
def endpoint():
    pass
```

### Dynamic Limits

Vary limits based on user authentication:

```python
def dynamic_limit():
    if current_user.is_authenticated and current_user.is_admin:
        return "1000 per hour"  # Higher limit for admins
    elif current_user.is_authenticated:
        return "100 per hour"   # Normal users
    return "10 per hour"        # Anonymous users

@app.route('/api/endpoint')
@limiter.limit(dynamic_limit)
def endpoint():
    pass
```

---

## Monitoring Rate Limits

### Check Current Usage

Rate limit headers are automatically included in responses:

```bash
curl -I http://localhost:8080/api/chat

# Response headers:
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1705612800
```

### Logging Rate Limit Violations

Add logging for rate limit violations:

```python
@app.errorhandler(429)
def ratelimit_handler(e):
    app.logger.warning(f"Rate limit exceeded: {request.remote_addr} on {request.endpoint}")
    return jsonify({
        'error': 'ratelimit exceeded',
        'message': str(e.description)
    }), 429
```

---

## Testing Rate Limits

### Test Login Rate Limit

```bash
# Try to login 6 times rapidly (limit is 5/minute)
for i in {1..6}; do
  curl -X POST http://localhost:8080/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n"
  sleep 1
done

# Expected: First 5 succeed (or fail with 401), 6th returns 429
```

### Test API Rate Limit

```bash
# Rapidly call API endpoint
for i in {1..35}; do
  curl -X POST http://localhost:8080/api/chat \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"test"}]}' \
    -w "\nStatus: %{http_code}\n"
  sleep 1
done

# Expected: First 30 succeed, 31+ return 429
```

---

## Files Modified

1. `unified_server.py` - Initialized limiter, added decorators to LLM endpoints
2. `auth_rate_limits.py` (NEW) - Rate limit configuration for auth routes
3. `requirements.txt` - Added `flask-limiter==3.5.0`

---

## Troubleshooting

### Rate Limits Not Working

1. **Check limiter is initialized:**
   ```python
   print(app.limiter)  # Should show Limiter instance
   ```

2. **Verify decorator is applied:**
   ```python
   print(app.view_functions['endpoint'].__dict__)
   ```

3. **Check storage:**
   ```bash
   # If using Redis
   redis-cli ping  # Should return PONG
   ```

### False Positives (Legitimate Users Blocked)

- Increase limits for authenticated users
- Use Redis for more accurate distributed rate limiting
- Consider using moving-window strategy instead of fixed-window

### Rate Limits Too Lenient

- Decrease per-minute limits
- Add per-second limits for very sensitive endpoints
- Monitor logs for abuse patterns

---

## Security Best Practices

1. ✅ **Different limits for different endpoints** - More sensitive = stricter limits
2. ✅ **Authenticated vs anonymous** - Higher limits for logged-in users
3. ✅ **Monitor and adjust** - Review logs, adjust limits based on usage patterns
4. ✅ **Combine with other protections** - Use with CSRF, strong passwords, etc.
5. ✅ **Fail gracefully** - Return clear error messages, not generic 500 errors

---

## Next Steps

### Recommended Improvements

1. **Upgrade to Redis** for production multi-server deployments
2. **Add custom error pages** for 429 errors
3. **Implement exponential backoff** for repeated violations
4. **Monitor rate limit violations** in analytics dashboard
5. **Add IP whitelisting** for trusted services/IPs

---

**Last Updated:** 2025-01-18
**Implemented By:** Claude Code
