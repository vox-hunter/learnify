"""
Utilities package for Learnify application.
Contains common functionality used across the application.
"""

from .common_styles import apply_common_styles, get_base_styles, get_sidebar_styles, hide_navigation_links
from .lazy_imports import lazy_import, import_optional, prefetch_modules
from .background_jobs import start_course_generation, get_job, cleanup_finished
from .navigation_cache import record_page_visit, cache_course_list, get_cached_course_list, purge_stale_course_cache, warm_next_pages, remove_course_from_cache

__all__ = [
    'apply_common_styles',
    'get_base_styles', 
    'get_sidebar_styles',
    'hide_navigation_links',
    'lazy_import',
    'import_optional',
    'prefetch_modules',
    'start_course_generation',
    'get_job',
    'cleanup_finished',
    'record_page_visit',
    'cache_course_list',
    'get_cached_course_list',
    'purge_stale_course_cache',
    'warm_next_pages',
    'remove_course_from_cache'
]