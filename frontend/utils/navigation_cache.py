"""Navigation & page transition optimization helpers.

Implements lightweight client-side like routing optimizations using
Streamlit session_state caching. This reduces DB hits and prevents
expensive re-computation when switching between pages quickly.

Functions kept deliberately tiny to avoid import overhead.
"""
from __future__ import annotations
from typing import Any, List, Optional
import time
import streamlit as st

COURSE_LIST_TTL = 60  # seconds
LIKELY_NEXT_PAGE_KEY = "_likely_next_pages"


def _ensure_structures() -> None:
    if "course_cache" not in st.session_state:
        st.session_state.course_cache = {}
    if "course_list_cache" not in st.session_state:
        st.session_state.course_list_cache = {"data": None, "ts": 0.0}
    if LIKELY_NEXT_PAGE_KEY not in st.session_state:
        st.session_state[LIKELY_NEXT_PAGE_KEY] = []
    if "nav_perf" not in st.session_state:
        st.session_state.nav_perf = {"last_page": None, "ts": time.time()}


def record_page_visit(page_name: str) -> None:
    _ensure_structures()
    st.session_state.nav_perf["last_page"] = page_name
    st.session_state.nav_perf["ts"] = time.time()
    # Simple prediction model: static mapping for now
    predictions = {
        "New Course": ["Course", "Account", "Login"],
        "Login": ["New Course", "Course"],
        "Account": ["New Course", "Course"],
        "Course": ["New Course", "Account"],
    }
    st.session_state[LIKELY_NEXT_PAGE_KEY] = predictions.get(page_name, ["New Course"])[:3]


def get_likely_next_pages() -> List[str]:
    _ensure_structures()
    return st.session_state[LIKELY_NEXT_PAGE_KEY]


def get_cached_course(course_id: str):
    _ensure_structures()
    return st.session_state.course_cache.get(course_id)


def cache_course(course_id: str, data: Any) -> None:
    if not course_id or data is None:
        return
    _ensure_structures()
    st.session_state.course_cache[course_id] = data


def get_cached_course_list(force: bool = False):
    _ensure_structures()
    cache = st.session_state.course_list_cache
    now = time.time()
    if (not force and cache["data"] is not None and (now - cache["ts"]) < COURSE_LIST_TTL):
        return cache["data"]
    return None


def cache_course_list(courses) -> None:
    _ensure_structures()
    st.session_state.course_list_cache = {"data": courses, "ts": time.time()}


def invalidate_course_list_cache() -> None:
    """Force the next access to re-fetch course list from DB by clearing cache."""
    _ensure_structures()
    st.session_state.course_list_cache = {"data": None, "ts": 0.0}


def purge_stale_course_cache(valid_ids: Optional[List[str]] = None) -> None:
    _ensure_structures()
    if not valid_ids:
        return
    to_delete = [cid for cid in st.session_state.course_cache.keys() if cid not in valid_ids]
    for cid in to_delete:
        del st.session_state.course_cache[cid]

def remove_course_from_cache(course_id: str) -> None:
    """Remove a single course from both the course list cache and individual cache."""
    if not course_id:
        return
    _ensure_structures()
    # Remove from individual cache
    if course_id in st.session_state.course_cache:
        del st.session_state.course_cache[course_id]
    # Update list cache
    cache = st.session_state.course_list_cache
    data = cache.get("data") if isinstance(cache, dict) else None
    if data:
        filtered = [c for c in data if str(c.get('_id') or c.get('id') or c.get('course_id')) != course_id]
        if len(filtered) != len(data):
            st.session_state.course_list_cache = {"data": filtered, "ts": cache.get("ts", 0.0)}


def warm_next_pages(prefetch_fn=None) -> None:
    """Eagerly touch data for likely next pages.
    prefetch_fn is a callable taking (page_name) allowing callers to
    pre-warm extra resources (e.g., course manager, auth)."""
    if not prefetch_fn:
        return
    for page in get_likely_next_pages():
        try:
            prefetch_fn(page)
        except (RuntimeError, ValueError):
            pass
