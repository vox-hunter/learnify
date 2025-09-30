"""
Performance testing script for Learnify
This script helps verify that optimizations are working correctly
"""
import subprocess
import time
import requests
import sys
import os

def test_local_startup():
    """Test how quickly the local Streamlit app starts"""
    print("🧪 Testing local application startup...")
    
    start_time = time.time()
    
    # Start Streamlit in background
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/main.py",
            "--server.port", "8502",
            "--server.headless", "true",
            "--logger.level", "error"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for app to be ready
        max_wait = 30  # seconds
        app_ready = False
        
        for _ in range(max_wait):
            try:
                response = requests.get("http://localhost:8502/_stcore/health", timeout=1)
                if response.status_code == 200:
                    app_ready = True
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        startup_time = time.time() - start_time
        
        if app_ready:
            print(f"✅ Local app started in {startup_time:.2f} seconds")
            
            # Test initial page load
            try:
                page_start = time.time()
                response = requests.get("http://localhost:8502", timeout=10)
                page_load_time = time.time() - page_start
                
                if response.status_code == 200:
                    print(f"✅ Initial page load: {page_load_time:.2f} seconds")
                    
                    # Check if optimizations are present
                    content = response.text
                    optimizations_found = []
                    
                    if "Performance Optimized GA" in content:
                        optimizations_found.append("✅ Optimized Google Analytics")
                    else:
                        optimizations_found.append("❌ Google Analytics not optimized")
                    
                    if "Performance Hints Added" in content:
                        optimizations_found.append("✅ Performance hints present")
                    else:
                        optimizations_found.append("❌ Performance hints missing")
                    
                    if "preconnect" in content:
                        optimizations_found.append("✅ Resource preconnect hints")
                    else:
                        optimizations_found.append("❌ Missing preconnect hints")
                    
                    print("\n📊 Optimization Status:")
                    for opt in optimizations_found:
                        print(f"   {opt}")
                    
                else:
                    print(f"❌ Page load failed with status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to load page: {e}")
        else:
            print(f"❌ App failed to start within {max_wait} seconds")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        return startup_time if app_ready else None
        
    except Exception as e:
        print(f"❌ Error testing startup: {e}")
        return None

def check_config_file():
    """Check if the Streamlit config file was created correctly"""
    print("\n🔧 Checking Streamlit configuration...")
    
    config_path = os.path.expanduser("~/.streamlit/config.toml")
    
    if os.path.exists(config_path):
        print(f"✅ Config file exists: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Check for key optimizations
            optimizations = [
                ("enableWebsocketCompression = true", "WebSocket compression"),
                ("gatherUsageStats = false", "Usage stats disabled"),
                ("caching = true", "Client caching enabled"),
                ("level = \"ERROR\"", "Logging optimized")
            ]
            
            for setting, description in optimizations:
                if setting in config_content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ Missing: {description}")
                    
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
    else:
        print(f"❌ Config file not found at {config_path}")

def test_production_performance():
    """Test the production deployment performance"""
    print("\n🌐 Testing production deployment...")
    
    url = "https://learnify-pr-34.onrender.com"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Production site responds in {load_time:.2f} seconds")
            
            # Check response headers for performance optimizations
            headers = response.headers
            
            if 'cache-control' in headers:
                print(f"   ✅ Cache-Control: {headers['cache-control']}")
            
            if 'content-encoding' in headers:
                print(f"   ✅ Content-Encoding: {headers['content-encoding']}")
            
            # Check content size
            content_size = len(response.content)
            print(f"   📊 Page size: {content_size:,} bytes ({content_size/1024:.1f} KB)")
            
            # Look for optimization markers
            content = response.text
            if "Performance Optimized GA" in content:
                print("   ✅ Optimized analytics detected in production")
            else:
                print("   ⚠️ Optimizations may not be deployed yet")
                
        else:
            print(f"❌ Production site returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to reach production site: {e}")

def main():
    """Run all performance tests"""
    print("🚀 Learnify Performance Test Suite")
    print("=" * 50)
    
    # Check config
    check_config_file()
    
    # Test local performance
    startup_time = test_local_startup()
    
    # Test production
    test_production_performance()
    
    print("\n" + "=" * 50)
    print("📊 Performance Test Summary:")
    
    if startup_time:
        if startup_time < 5:
            print("✅ Local startup performance: Excellent")
        elif startup_time < 10:
            print("⚠️ Local startup performance: Good")
        else:
            print("❌ Local startup performance: Needs improvement")
    
    print("\n💡 Performance Tips:")
    print("- Initial page loads may still be slow due to Render.com cold starts")
    print("- The optimizations will show most benefit on subsequent page loads")
    print("- Monitor Core Web Vitals in browser dev tools for detailed metrics")
    print("- Consider upgrading Render.com plan for better performance")

if __name__ == "__main__":
    main()