# Deployment Guide for Streamlit Multipage Routing

This guide provides specific instructions for deploying the routing fix across different platforms.

## Quick Fix for Common Platforms

### Streamlit Cloud
Since server configuration isn't available, use query parameters instead:
- Share links as: `https://yourapp.streamlit.app/?page=privacy`
- The JavaScript will detect and route appropriately

### Heroku
Add a `_redirects` file or use nginx buildpack:
```
/privacy /
/terms /
/course /
/login /
```

### Vercel
Create `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/privacy", "destination": "/" },
    { "source": "/terms", "destination": "/" },
    { "source": "/course", "destination": "/" },
    { "source": "/login", "destination": "/" }
  ]
}
```

### Netlify
Create `_redirects` file:
```
/privacy / 200
/terms / 200
/course / 200
/login / 200
```

### Docker
Use nginx as reverse proxy with provided `streamlit_rewrite.conf`.

Example `docker-compose.yml`:
```yaml
version: '3'
services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
  
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./streamlit_rewrite.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - streamlit
```

### AWS/GCP Load Balancers
Configure path-based routing to forward all requests to your Streamlit instance.

## Testing Your Deployment

After deployment, test these URLs:
- `https://yourapp.com/privacy` - Should show Privacy Policy
- `https://yourapp.com/terms` - Should show Terms & Conditions
- `https://yourapp.com/course` - Should show Course page (if accessible)

## Troubleshooting

### Still Getting 404s?
1. Verify server configuration is applied and active
2. Check web server logs for routing issues
3. Ensure Streamlit app is running on expected port
4. Test with query parameters: `?_route_to=Privacy`

### JavaScript Not Working?
1. Check browser console for errors
2. Verify the JavaScript code is being loaded
3. Test on different browsers
4. Use development tools to debug routing logic

### Internal Navigation Broken?
1. Check for JavaScript errors in console
2. Verify Streamlit session state isn't corrupted
3. Clear browser cache and cookies
4. Restart Streamlit application

## Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Internal Navigation | ✅ Works | ✅ Works |
| Direct URL Access | ⚠️ Limited | ✅ Full Support* |
| JavaScript Routing | ✅ Enhanced | ✅ Enhanced |
| Server Configuration | ❌ Not Required | ✅ Required |

*Requires proper server configuration

## Security Considerations

- Server-side redirects are secure and don't expose routing logic
- Client-side routing is visible but doesn't compromise security
- Always validate user permissions on protected pages
- Consider rate limiting for public routes

## Performance Notes

- Server-side redirects are faster than JavaScript routing
- Client-side routing adds minimal overhead
- Nginx configuration is more efficient than Apache for high traffic
- Consider caching strategies for static routes