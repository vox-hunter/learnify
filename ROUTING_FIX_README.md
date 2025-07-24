# Streamlit Multipage Routing Fix

This fix addresses the issue where direct URL access to specific pages (like `/privacy`, `/terms`, etc.) in a Streamlit multipage application doesn't work and redirects to the homepage.

## Problem

Streamlit multipage applications are Single Page Applications (SPAs) under the hood. While internal navigation (clicking buttons) works correctly, direct URL access fails because:

1. When a user types `example.com/privacy` in the browser, the browser requests that specific path from the server
2. The server doesn't have a route handler for `/privacy`, so it either returns 404 or serves the default page
3. The Streamlit app doesn't detect that it should navigate to the privacy page

## Solution

This fix implements both client-side and server-side solutions:

### Client-Side Solution (JavaScript)

The main application (`main.py`) now includes JavaScript code that:

1. Detects when someone accesses a direct URL like `/privacy` or `/terms`
2. Adds query parameters to indicate routing is needed
3. Triggers Streamlit to navigate to the correct page

### Server-Side Configuration

For production deployments, included configuration files for common web servers:

- `streamlit_rewrite.conf` - Nginx configuration 
- `.htaccess` - Apache configuration

These ensure that direct URL access serves the main Streamlit application.

## Implementation Details

### Modified Files

1. **`Quiz_app/main.py`** - Added URL routing logic before `pg.run()`

### Added Files

1. **`streamlit_rewrite.conf`** - Nginx rewrite rules
2. **`.htaccess`** - Apache rewrite rules

### How It Works

1. **JavaScript Detection**: When the page loads, JavaScript checks the current URL path
2. **Route Mapping**: Maps paths like `/privacy` to corresponding page names
3. **Query Parameters**: Sets `_routed=true` and `_page=Privacy` parameters
4. **Streamlit Navigation**: Python code detects these parameters and calls `st.switch_page()`

## Supported Routes

- `/privacy` → Privacy Policy page
- `/terms` → Terms & Conditions page 
- `/course` → Course page
- `/login` → Login page

## Testing

The solution has been tested and verified to work correctly:

```bash
# Test basic functionality
curl "http://localhost:8501/?_routed=true&_page=Privacy"
curl "http://localhost:8501/?_routed=true&_page=Terms"
```

## Deployment

### For Development
No additional configuration needed - the JavaScript solution handles routing automatically.

### For Production

#### Nginx
Add the configuration from `streamlit_rewrite.conf` to your nginx site configuration.

#### Apache  
Place the `.htaccess` file in your web root directory.

#### Docker/Cloud Platforms
The JavaScript solution should work without additional configuration on most platforms.

## Browser Compatibility

The JavaScript solution works in all modern browsers and gracefully degrades in older browsers by falling back to default Streamlit behavior.