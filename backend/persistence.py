"""
backend/persistence.py — Supabase persistence layer with robust local fallback.

Stores and retrieves branches, canonical custom tasks, and scenario runs.
Uses Supabase PostgREST API over HTTP if SUPABASE_URL and key are provided;
otherwise transparently falls back to an in-memory/cached store so local
development, testing, and offline modes work seamlessly without crashing.
"""

from __future__ import annotations

import datetime
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Canonical default tasks matching system defaults
DEFAULT_BRANCH = {
    "id": "branch-main",
    "name": "Downtown Main Branch",
    "location": "Financial District, Metro Central",
    "created_at": "2026-09-10T00:00:00Z",
    "updated_at": "2026-09-10T00:00:00Z",
}

INITIAL_TASKS = [
    {
        "id": "task-default-1",
        "branch_id": "branch-main",
        "task_type": "teller",
        "task_name": "Cash Deposit & Withdrawal",
        "customers_per_hour": 12.0,
        "average_service_time_minutes": 3.5,
        "created_at": "2026-09-10T00:00:00Z",
        "updated_at": "2026-09-10T00:00:00Z",
    },
    {
        "id": "task-default-2",
        "branch_id": "branch-main",
        "task_type": "teller",
        "task_name": "Bill Pay & Check Cashing",
        "customers_per_hour": 8.0,
        "average_service_time_minutes": 4.0,
        "created_at": "2026-09-10T00:00:00Z",
        "updated_at": "2026-09-10T00:00:00Z",
    },
    {
        "id": "task-default-3",
        "branch_id": "branch-main",
        "task_type": "loan",
        "task_name": "Personal & Auto Loan Consultation",
        "customers_per_hour": 3.2,
        "average_service_time_minutes": 20.0,
        "created_at": "2026-09-10T00:00:00Z",
        "updated_at": "2026-09-10T00:00:00Z",
    },
    {
        "id": "task-default-4",
        "branch_id": "branch-main",
        "task_type": "loan",
        "task_name": "Mortgage Pre-Approval Application",
        "customers_per_hour": 1.6,
        "average_service_time_minutes": 25.0,
        "created_at": "2026-09-10T00:00:00Z",
        "updated_at": "2026-09-10T00:00:00Z",
    },
    {
        "id": "task-default-5",
        "branch_id": "branch-main",
        "task_type": "customer_service",
        "task_name": "Account Opening & Onboarding",
        "customers_per_hour": 4.5,
        "average_service_time_minutes": 12.0,
        "created_at": "2026-09-10T00:00:00Z",
        "updated_at": "2026-09-10T00:00:00Z",
    },
    {
        "id": "task-default-6",
        "branch_id": "branch-main",
        "task_type": "customer_service",
        "task_name": "Card Replacement & KYC Update",
        "customers_per_hour": 5.5,
        "average_service_time_minutes": 8.0,
        "created_at": "2026-09-10T00:00:00Z",
        "updated_at": "2026-09-10T00:00:00Z",
    },
]


class PersistenceManager:
    """
    Manages persistence to Supabase with in-memory fallback.
    """

    def __init__(self) -> None:
        self.supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        )

        # In-memory storage for fallback / local testing
        self._local_branches: Dict[str, Dict[str, Any]] = {
            DEFAULT_BRANCH["id"]: dict(DEFAULT_BRANCH)
        }
        self._local_tasks: Dict[str, Dict[str, Any]] = {
            t["id"]: dict(t) for t in INITIAL_TASKS
        }
        self._local_scenarios: List[Dict[str, Any]] = []

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def get_status(self) -> Dict[str, Any]:
        """Check persistence layer connectivity."""
        if not self.is_supabase_configured:
            return {
                "connected": True,
                "mode": "local_fallback",
                "message": "Running on local deterministic persistence (SUPABASE_URL not configured).",
            }

        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(
                    f"{self.supabase_url}/rest/v1/branches?select=id&limit=1",
                    headers=self._get_headers(),
                )
                if res.is_success:
                    return {
                        "connected": True,
                        "mode": "supabase",
                        "message": "Connected to Supabase PostgreSQL database.",
                        "endpoint": self.supabase_url,
                    }
                else:
                    return {
                        "connected": False,
                        "mode": "supabase_error",
                        "status_code": res.status_code,
                        "message": f"Supabase responded with error HTTP {res.status_code}. Using local store.",
                    }
        except Exception as exc:
            return {
                "connected": False,
                "mode": "supabase_offline",
                "message": f"Could not reach Supabase endpoint ({exc}). Operating on local fallback.",
            }

    # ---------------------------------------------------------------------------
    # Branches CRUD
    # ---------------------------------------------------------------------------
    def get_branches(self) -> List[Dict[str, Any]]:
        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.get(
                        f"{self.supabase_url}/rest/v1/branches?select=*&order=created_at.asc",
                        headers=self._get_headers(),
                    )
                    if res.is_success:
                        data = res.json()
                        if data:
                            return data
            except Exception as exc:
                logger.warning("Supabase get_branches failed: %s. Using local store.", exc)

        return list(self._local_branches.values())

    def create_branch(self, name: str, location: str) -> Dict[str, Any]:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        branch_id = f"branch-{uuid.uuid4().hex[:8]}"
        payload = {
            "id": branch_id,
            "name": name,
            "location": location,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.post(
                        f"{self.supabase_url}/rest/v1/branches",
                        headers=self._get_headers(),
                        json=payload,
                    )
                    if res.is_success:
                        items = res.json()
                        return items[0] if items else payload
            except Exception as exc:
                logger.warning("Supabase create_branch failed: %s. Storing locally.", exc)

        self._local_branches[branch_id] = payload
        return payload

    # ---------------------------------------------------------------------------
    # Branch Tasks CRUD
    # ---------------------------------------------------------------------------
    def get_branch_tasks(self, branch_id: str) -> List[Dict[str, Any]]:
        # Normalize branch_id
        if branch_id == "default":
            branch_id = "branch-main"

        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.get(
                        f"{self.supabase_url}/rest/v1/branch_tasks?branch_id=eq.{branch_id}&select=*&order=created_at.asc",
                        headers=self._get_headers(),
                    )
                    if res.is_success:
                        tasks = res.json()
                        if tasks:
                            return tasks
            except Exception as exc:
                logger.warning("Supabase get_branch_tasks failed: %s. Using local store.", exc)

        return [t for t in self._local_tasks.values() if t["branch_id"] == branch_id]

    def create_branch_task(self, branch_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        if branch_id == "default":
            branch_id = "branch-main"

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        task_id = task.get("id") or f"task-{uuid.uuid4().hex[:8]}"

        payload = {
            "id": task_id,
            "branch_id": branch_id,
            "task_type": task["task_type"],
            "task_name": task["task_name"],
            "customers_per_hour": float(task["customers_per_hour"]),
            "average_service_time_minutes": float(task["average_service_time_minutes"]),
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.post(
                        f"{self.supabase_url}/rest/v1/branch_tasks",
                        headers=self._get_headers(),
                        json=payload,
                    )
                    if res.is_success:
                        items = res.json()
                        return items[0] if items else payload
            except Exception as exc:
                logger.warning("Supabase create_branch_task failed: %s. Storing locally.", exc)

        self._local_tasks[task_id] = payload
        return payload

    def update_branch_task(
        self, branch_id: str, task_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if branch_id == "default":
            branch_id = "branch-main"

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        patch_data = dict(updates)
        patch_data["updated_at"] = now_iso

        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.patch(
                        f"{self.supabase_url}/rest/v1/branch_tasks?id=eq.{task_id}&branch_id=eq.{branch_id}",
                        headers=self._get_headers(),
                        json=patch_data,
                    )
                    if res.is_success:
                        items = res.json()
                        if items:
                            return items[0]
            except Exception as exc:
                logger.warning("Supabase update_branch_task failed: %s. Updating locally.", exc)

        if task_id in self._local_tasks and self._local_tasks[task_id]["branch_id"] == branch_id:
            self._local_tasks[task_id].update(patch_data)
            return self._local_tasks[task_id]

        return None

    def delete_branch_task(self, branch_id: str, task_id: str) -> bool:
        if branch_id == "default":
            branch_id = "branch-main"

        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.delete(
                        f"{self.supabase_url}/rest/v1/branch_tasks?id=eq.{task_id}&branch_id=eq.{branch_id}",
                        headers=self._get_headers(),
                    )
                    if res.is_success:
                        return True
            except Exception as exc:
                logger.warning("Supabase delete_branch_task failed: %s. Deleting locally.", exc)

        if task_id in self._local_tasks and self._local_tasks[task_id]["branch_id"] == branch_id:
            del self._local_tasks[task_id]
            return True
        return False

    # ---------------------------------------------------------------------------
    # Scenario Runs CRUD
    # ---------------------------------------------------------------------------
    def save_scenario_run(
        self,
        branch_id: str,
        scenario_type: str,
        scenario_name: str,
        input_snapshot: Dict[str, Any],
        result_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        if branch_id == "default":
            branch_id = "branch-main"

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        scenario_id = f"scenario-{uuid.uuid4().hex[:10]}"
        payload = {
            "id": scenario_id,
            "branch_id": branch_id,
            "scenario_type": scenario_type,
            "scenario_name": scenario_name,
            "input_snapshot": input_snapshot,
            "result_snapshot": result_snapshot,
            "created_at": now_iso,
        }

        if self.is_supabase_configured:
            try:
                with httpx.Client(timeout=3.0) as client:
                    res = client.post(
                        f"{self.supabase_url}/rest/v1/scenario_runs",
                        headers=self._get_headers(),
                        json=payload,
                    )
                    if res.is_success:
                        items = res.json()
                        return items[0] if items else payload
            except Exception as exc:
                logger.warning("Supabase save_scenario_run failed: %s. Storing locally.", exc)

        self._local_scenarios.insert(0, payload)
        return payload

    def get_scenario_runs(
        self, branch_id: str, scenario_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if branch_id == "default":
            branch_id = "branch-main"

        if self.is_supabase_configured:
            try:
                query = f"branch_id=eq.{branch_id}&select=*&order=created_at.desc"
                if scenario_type:
                    query += f"&scenario_type=eq.{scenario_type}"
                with httpx.Client(timeout=3.0) as client:
                    res = client.get(
                        f"{self.supabase_url}/rest/v1/scenario_runs?{query}",
                        headers=self._get_headers(),
                    )
                    if res.is_success:
                        return res.json()
            except Exception as exc:
                logger.warning("Supabase get_scenario_runs failed: %s. Using local store.", exc)

        runs = [s for s in self._local_scenarios if s["branch_id"] == branch_id]
        if scenario_type:
            runs = [s for s in runs if s["scenario_type"] == scenario_type]
        return runs


# Singleton instance used throughout backend
db = PersistenceManager()
