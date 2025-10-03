# Installation helper for file conversion dependencies
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def install_conversion_dependencies():
    """
    Install required packages for file conversion functionality.
    """
    
    required_packages = [
        'reportlab',      # PDF generation
        'python-docx',    # Word document processing
        'python-pptx',    # PowerPoint processing
        'pandas',         # Excel processing
        'openpyxl',       # Excel processing
        'pillow',         # Image processing
    ]
    
    installed_packages = []
    failed_packages = []
    
    for package in required_packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            installed_packages.append(package)
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            failed_packages.append(package)
    
    return installed_packages, failed_packages

def check_conversion_dependencies():
    """
    Check which conversion dependencies are available.
    """
    dependencies = {
        'reportlab': False,
        'python-docx': False, 
        'python-pptx': False,
        'pandas': False,
        'openpyxl': False,
        'pillow': False,
    }
    
    for package in dependencies:
        try:
            if package == 'python-docx':
                import docx
            elif package == 'python-pptx':
                import pptx
            elif package == 'pillow':
                import PIL
            else:
                __import__(package)
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies

if __name__ == "__main__":
    print("Checking conversion dependencies...")
    deps = check_conversion_dependencies()
    
    missing = [pkg for pkg, available in deps.items() if not available]
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing missing packages...")
        installed, failed = install_conversion_dependencies()
        
        if installed:
            print(f"Successfully installed: {', '.join(installed)}")
        if failed:
            print(f"Failed to install: {', '.join(failed)}")
    else:
        print("All conversion dependencies are available!")
