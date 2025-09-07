"""Background job management for long-running operations (course generation).

Refactored to use a process-wide cached registry (st.cache_resource)
instead of per-session st.session_state. This avoids accessing
session_state from worker threads (which raises Missing ScriptRunContext
and KeyErrors) while still allowing polling from the UI.
"""
from __future__ import annotations
import threading
import time
import uuid
from typing import Optional, Callable, Dict, Any
import streamlit as st


@st.cache_resource
def _job_store():
    return {"jobs": {}, "lock": threading.Lock()}


def _now() -> float:
    return time.time()


def start_course_generation(file_content: Optional[bytes] = None,
                             file_stream: Optional[Any] = None,
                             file_url: Optional[str] = None,
                             filename: Optional[str] = None,
                             user_context: Optional[Dict[str, Any]] = None,
                             generate_course_fn: Optional[Callable] = None) -> str:
    """Start a background course generation job.

    generate_course_fn must accept (file_content=None, file_url=None, filename=None, status_callback=None)
    and return (course_data, error_message).
    """
    store = _job_store()
    jobs = store["jobs"]
    lock = store["lock"]
    job_id = str(uuid.uuid4())
    with lock:
        # Initialize job with minimal non-zero progress so UI shows activity sooner
        jobs[job_id] = {
            "type": "course_generation",
            "status": "queued",
            "progress": 1,
            "message": "Queued",
            "result": None,
            "error": None,
            "started_at": None,
            "finished_at": None,
            "filename": filename,
            "file_url": file_url,
            "file_stream": bool(file_stream),  # store presence flag only (uploaded file objects not cacheable / picklable)
            "user_context": user_context or {},
        }

    def _update(message: str, progress: Optional[int]):
        with lock:
            job = jobs.get(job_id)
            if not job:
                return
            if progress is not None:
                job["progress"] = max(0, min(100, int(progress)))
            job["message"] = message

    def _worker():
        with lock:
            job = jobs.get(job_id)
            if not job:
                return
            job["status"] = "running"
            job["started_at"] = _now()
            # Bump progress a little on start to differentiate from queued
            if job["progress"] < 3:
                job["progress"] = 3
                job["message"] = "Starting"
        try:
            if not generate_course_fn:
                raise RuntimeError("generate_course_fn not provided")
            # Pass file_stream if provided (some backends may support chunked streaming)
            kwargs = dict(
                file_content=file_content,
                file_url=file_url,
                filename=filename,
                status_callback=_update,
            )
            if file_stream is not None:
                kwargs["file_stream"] = file_stream
            course_data, error_message = generate_course_fn(**kwargs)
            with lock:
                job = jobs.get(job_id)
                if not job:
                    return
                if error_message:
                    job["status"] = "error"
                    job["error"] = error_message
                    job["progress"] = max(job["progress"], 100)
                    job["message"] = f"Failed: {error_message[:120]}"
                else:
                    job["status"] = "done"
                    job["result"] = course_data
                    job["progress"] = 100
                    job["message"] = "Course generated"
        except (RuntimeError, ValueError, TypeError, OSError) as e:
            # Handle common expected exceptions explicitly; allow truly unexpected ones to surface
            with lock:
                job = jobs.get(job_id)
                if job:
                    job["status"] = "error"
                    job["error"] = str(e)
                    job["message"] = f"Error: {e}"[:140]
                    job["progress"] = 100
        finally:
            with lock:
                job = jobs.get(job_id)
                if job:
                    job["finished_at"] = _now()

    threading.Thread(target=_worker, name=f"course-gen-{job_id[:8]}", daemon=True).start()
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    store = _job_store()
    with store["lock"]:
        job = store["jobs"].get(job_id)
        return dict(job) if job else None


def list_jobs(job_type: Optional[str] = None):
    store = _job_store()
    with store["lock"]:
        jobs = store["jobs"]
        if job_type:
            return {jid: dict(j) for jid, j in jobs.items() if j.get("type") == job_type}
        return {jid: dict(j) for jid, j in jobs.items()}


def cleanup_finished(older_than_seconds: int = 3600):
    store = _job_store()
    now = _now()
    with store["lock"]:
        to_delete = []
        for jid, job in store["jobs"].items():
            if job.get("finished_at") and (now - job["finished_at"]) > older_than_seconds:
                to_delete.append(jid)
        for jid in to_delete:
            del store["jobs"][jid]


def _self_test_dummy(duration: float = 0.5):  # pragma: no cover - auxiliary
    """Run a very small dummy job to validate background infrastructure.

    Returns the final job dict.
    """
    def _dummy_generate_course_fn(file_content=None, file_url=None, filename=None, status_callback=None):  # noqa: D401, ARG001
        steps = [
            ("Preparing", 10),
            ("Processing", 50),
            ("Refining", 80),
            ("Finalizing", 95),
        ]
        for msg, prog in steps:
            if status_callback:
                status_callback(msg, prog)
            time.sleep(duration / len(steps))
        if status_callback:
            status_callback("Done", 100)
        return {"ok": True}, None

    job_id = start_course_generation(generate_course_fn=_dummy_generate_course_fn)
    # Poll until done or timeout
    deadline = time.time() + 5
    while time.time() < deadline:
        job = get_job(job_id)
        if job and job.get("status") in {"done", "error"}:
            return job
        time.sleep(0.05)
    return get_job(job_id)
