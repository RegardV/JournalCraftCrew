# Cloudflare Setup for Journal Craft Crew

## 1. Create Cloudflare Account
1. Go to: https://cloudflare.com
2. Sign up for FREE account
3. Add your domain (e.g., journalcraftcrew.com)

## 2. Update DNS Records
```
Type: A Record
Name: @ (your domain)
Content: [Google Cloud Run IP]
Proxy: Enabled (orange cloud)

Type: A Record
Name: api
Content: [Google Cloud Run Backend IP]
Proxy: Enabled (orange cloud)

Type: CNAME
Name: www
Content: yourdomain.com
Proxy: Enabled (orange cloud)
```

## 3. SSL/TLS Configuration
- Go to: SSL/TLS → Overview
- Set to: **Full (Strict)**
- This ensures end-to-end encryption

## 4. Page Rules for Caching
```
Rule 1: Cache static assets
If URL matches: *.js, *.css, *.png, *.jpg, *.pdf
Then: Cache Level: Everything
Edge Cache TTL: 1 month

Rule 2: API endpoints
If URL matches: /api/*
Then: Bypass Cache
Cache Level: Bypass

Rule 3: Dynamic content
If URL matches: /*
Then: Cache Level: Standard
Edge Cache TTL: 4 hours
```

## 5. Cloudflare Workers (Optional)
```javascript
// Worker for API rate limiting
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Rate limiting logic here
    const clientId = request.headers.get('CF-Connecting-IP');
    // ... rate limiting implementation

    // Forward to Google Cloud Run
    const backend = 'https://your-backend-url.run.app';
    return fetch(backend + url.pathname + url.search, request);
  }
}
```

## 6. Analytics and Security
- Enable Cloudflare Analytics (FREE)
- Set up Web Application Firewall (WAF) rules
- Configure rate limiting
- Enable Bot Fight Mode

## Benefits Achieved:
✅ Free global CDN (reduces Google Cloud costs)
✅ Free SSL certificates
✅ 20x faster global performance
✅ Enterprise DDoS protection
✅ Free load balancing
✅ Advanced caching rules