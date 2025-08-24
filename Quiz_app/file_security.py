# File Security and Validation Module
# Handles file type restrictions and security validation

import os
import mimetypes
from typing import Tuple, Optional

# Maximum file size: 10MB (same as before)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# Maximum content length: 15,000 words (same as before)
MAX_CONTENT_WORDS = 15000

# Dangerous file extensions that should be blocked for security
DANGEROUS_EXTENSIONS = {
    # Executable files
    '.exe', '.bat', '.cmd', '.com', '.scr', '.msi', '.dll', '.pif',
    # Script files
    '.vbs', '.vbe', '.js', '.jse', '.ws', '.wsf', '.wsc', '.wsh',
    '.ps1', '.ps1xml', '.ps2', '.ps2xml', '.psc1', '.psc2',
    '.sh', '.bash', '.zsh', '.fish', '.csh', '.tcsh',
    '.py', '.pyw', '.pyc', '.pyo', '.pyd',
    # Archive files (can contain dangerous files)
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lzma',
    # System and configuration files
    '.sys', '.inf', '.reg', '.cfg', '.ini',
    # Disk images
    '.iso', '.img', '.dmg', '.vhd', '.vmdk',
    # Other potentially dangerous
    '.jar', '.deb', '.rpm', '.pkg', '.app'
}

# Safe file extensions that are explicitly allowed
SAFE_EXTENSIONS = {
    # Documents
    '.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt', '.pages',
    # Presentations
    '.pptx', '.ppt', '.odp', '.key',
    # Spreadsheets
    '.xlsx', '.xls', '.csv', '.ods', '.numbers',
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.heic', '.heif',
    # Audio
    '.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma',
    # Video
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp',
    # Text and markup
    '.md', '.markdown', '.json', '.xml', '.html', '.htm', '.yaml', '.yml', '.toml',
    # Other safe formats
    '.epub', '.mobi', '.azw', '.azw3'
}

# MIME types supported by Gemini AI (as of 2024)
GEMINI_SUPPORTED_MIME_TYPES = {
    # Documents
    'application/pdf',
    'text/plain',
    'text/html',
    'text/css',
    'text/javascript',
    'text/markdown',
    'application/rtf',
    # Images
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/webp',
    'image/heic',
    'image/heif',
    # Audio
    'audio/wav',
    'audio/mp3',
    'audio/aiff',
    'audio/aac',
    'audio/ogg',
    'audio/flac',
    # Video
    'video/mp4',
    'video/mpeg',
    'video/mov',
    'video/avi',
    'video/x-flv',
    'video/mpg',
    'video/webm',
    'video/wmv',
    'video/3gpp',
}

def get_mime_type(filename: str, file_content: Optional[bytes] = None) -> str:
    """
    Get MIME type for a file based on its extension and optionally content.
    Returns a MIME type that is compatible with Gemini AI.
    """
    # Note: file_content parameter reserved for future content-based detection
    _ = file_content  # Suppress unused parameter warning
    
    # Get MIME type from filename
    mime_type, _ = mimetypes.guess_type(filename)
    
    # If we got a MIME type and it's supported by Gemini, use it
    if mime_type and mime_type in GEMINI_SUPPORTED_MIME_TYPES:
        return mime_type
    
    # Fallback based on extension for Gemini-compatible types
    ext = os.path.splitext(filename.lower())[1]
    
    # Map extensions to Gemini-supported MIME types
    gemini_mime_map = {
        # Documents - map unsupported formats to supported ones
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.markdown': 'text/markdown',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.rtf': 'application/rtf',
        # For unsupported document formats, use generic binary
        '.docx': 'application/octet-stream',  # Gemini doesn't support this
        '.doc': 'application/octet-stream',   # Gemini doesn't support this
        '.pptx': 'application/octet-stream',  # Gemini doesn't support this
        '.ppt': 'application/octet-stream',   # Gemini doesn't support this
        '.xlsx': 'application/octet-stream',  # Gemini doesn't support this
        '.xls': 'application/octet-stream',   # Gemini doesn't support this
        '.csv': 'text/plain',                 # CSV can be treated as text
        # Images - supported by Gemini
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.heic': 'image/heic',
        '.heif': 'image/heif',
        # Images - not supported, use generic
        '.bmp': 'application/octet-stream',
        '.tiff': 'application/octet-stream',
        '.tif': 'application/octet-stream',
        '.svg': 'application/octet-stream',
        # Audio - supported by Gemini
        '.mp3': 'audio/mp3',
        '.wav': 'audio/wav',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        # Audio - not supported
        '.m4a': 'application/octet-stream',
        '.wma': 'application/octet-stream',
        # Video - supported by Gemini
        '.mp4': 'video/mp4',
        '.avi': 'video/avi',
        '.mov': 'video/mov',
        '.webm': 'video/webm',
        '.3gp': 'video/3gpp',
        # Video - not supported
        '.wmv': 'application/octet-stream',
        '.flv': 'application/octet-stream',
        '.mkv': 'application/octet-stream',
        '.m4v': 'application/octet-stream',
        # Other formats
        '.json': 'text/plain',  # Treat JSON as text
        '.xml': 'text/plain',   # Treat XML as text
        '.yaml': 'text/plain',  # Treat YAML as text
        '.yml': 'text/plain',   # Treat YAML as text
        '.toml': 'text/plain',  # Treat TOML as text
    }
    
    return gemini_mime_map.get(ext, 'application/octet-stream')

def validate_file_security(filename: str, file_size: int) -> Tuple[bool, str]:
    """
    Validate file for security issues.
    Returns (is_safe, error_message)
    """
    # Check file size limit (10MB)
    if file_size > MAX_FILE_SIZE:
        return False, f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds the maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB."
    
    # Get file extension
    _, ext = os.path.splitext(filename.lower())
    
    # Check if file extension is dangerous
    if ext in DANGEROUS_EXTENSIONS:
        return False, f"File type '{ext}' is not allowed for security reasons."
    
    # Check if file extension is explicitly safe
    if ext in SAFE_EXTENSIONS:
        return True, ""
    
    # For unknown extensions, be cautious but allow
    if ext == '':
        return False, "Files without extensions are not allowed."
    
    # Unknown but not explicitly dangerous - allow with warning
    return True, ""

def get_file_type_category(filename: str) -> str:
    """
    Get the category of file type for display purposes.
    """
    _, ext = os.path.splitext(filename.lower())
    
    if ext in {'.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt', '.pages'}:
        return "Document"
    elif ext in {'.pptx', '.ppt', '.odp', '.key'}:
        return "Presentation"
    elif ext in {'.xlsx', '.xls', '.csv', '.ods', '.numbers'}:
        return "Spreadsheet"
    elif ext in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.heic', '.heif'}:
        return "Image"
    elif ext in {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma'}:
        return "Audio"
    elif ext in {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp'}:
        return "Video"
    elif ext in {'.md', '.markdown', '.json', '.xml', '.html', '.htm', '.yaml', '.yml', '.toml'}:
        return "Text/Markup"
    else:
        return "Other"

def get_supported_file_types_display() -> str:
    """
    Get a user-friendly string of supported file types.
    """
    categories = {
        "Documents": "PDF, Text, Markdown, HTML, RTF",
        "Office Files": "Word, Excel, PowerPoint (processed as binary)",
        "Images": "PNG, JPEG, GIF, WebP, HEIC",
        "Audio": "MP3, WAV, AAC, FLAC, OGG", 
        "Video": "MP4, AVI, MOV, WebM, 3GP",
        "Other": "JSON, XML, YAML, CSV"
    }
    
    return " • ".join([f"{cat}: {types}" for cat, types in categories.items()])

def is_gemini_native_supported(filename: str) -> bool:
    """
    Check if a file type is natively supported by Gemini AI for content extraction.
    """
    mime_type = get_mime_type(filename)
    return mime_type in GEMINI_SUPPORTED_MIME_TYPES

def get_file_processing_info(filename: str) -> str:
    """
    Get information about how the file will be processed.
    """
    from document_converter import get_conversion_info
    return get_conversion_info(filename)

def estimate_content_words(file_size: int, file_extension: str) -> Optional[int]:
    """
    Estimate word count based on file size and type.
    This is a rough estimate since we can't extract content without processing.
    """
    ext = file_extension.lower()
    
    # Text-based files - rough estimate
    if ext in {'.txt', '.md', '.markdown', '.html', '.htm', '.xml', '.json', '.csv'}:
        # Assume average 5 characters per word + spaces
        estimated_words = file_size // 6
        return estimated_words
    
    # For other file types, we can't easily estimate without processing
    # Return None to indicate unknown
    return None
