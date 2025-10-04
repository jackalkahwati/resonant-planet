"""
Job management and execution.
"""
import uuid
import sqlite3
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class JobStore:
    """
    SQLite-based job status and results store.
    """

    def __init__(self, db_path: str = "resonant_worlds.db"):
        """
        Initialize job store.

        Parameters
        ----------
        db_path : str
            Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                dataset_id TEXT,
                status TEXT,
                progress REAL,
                stage TEXT,
                message TEXT,
                created_at TEXT,
                updated_at TEXT,
                params TEXT
            )
        """)

        # Candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id TEXT PRIMARY KEY,
                job_id TEXT,
                probability REAL,
                period_days REAL,
                t0_bjd REAL,
                depth_ppm REAL,
                duration_hours REAL,
                snr REAL,
                rl_action TEXT,
                flags TEXT,
                plots TEXT,
                created_at TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(job_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_job(self, dataset_id: str, params: Dict) -> str:
        """
        Create a new job.

        Parameters
        ----------
        dataset_id : str
            Dataset identifier
        params : Dict
            Run parameters

        Returns
        -------
        str
            Job ID
        """
        job_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO jobs (job_id, dataset_id, status, progress, stage, message, created_at, updated_at, params)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, dataset_id, "queued", 0.0, "queued", "Job created", now, now, json.dumps(params)),
        )

        conn.commit()
        conn.close()

        logger.info(f"Created job {job_id}")
        return job_id

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        progress: Optional[float] = None,
        stage: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Update job status.

        Parameters
        ----------
        job_id : str
            Job ID
        status : str, optional
            New status
        progress : float, optional
            Progress percentage
        stage : str, optional
            Current stage
        message : str, optional
            Status message
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if status is not None:
            updates.append("status = ?")
            values.append(status)

        if progress is not None:
            updates.append("progress = ?")
            values.append(progress)

        if stage is not None:
            updates.append("stage = ?")
            values.append(stage)

        if message is not None:
            updates.append("message = ?")
            values.append(message)

        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())

        values.append(job_id)

        cursor.execute(f"UPDATE jobs SET {', '.join(updates)} WHERE job_id = ?", values)

        conn.commit()
        conn.close()

    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job information.

        Parameters
        ----------
        job_id : str
            Job ID

        Returns
        -------
        Optional[Dict]
            Job information or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            job = dict(row)
            job["params"] = json.loads(job["params"])
            return job
        return None

    def add_candidate(self, job_id: str, candidate: Dict) -> str:
        """
        Add a candidate to the database.

        Parameters
        ----------
        job_id : str
            Job ID
        candidate : Dict
            Candidate information

        Returns
        -------
        str
            Candidate ID
        """
        candidate_id = candidate.get("candidate_id", str(uuid.uuid4()))
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO candidates 
            (candidate_id, job_id, probability, period_days, t0_bjd, depth_ppm, duration_hours, 
             snr, rl_action, flags, plots, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id,
                job_id,
                candidate["probability"],
                candidate["period_days"],
                candidate["t0_bjd"],
                candidate["depth_ppm"],
                candidate["duration_hours"],
                candidate["snr"],
                candidate["rl_action"],
                json.dumps(candidate["flags"]),
                json.dumps(candidate["plots"]),
                now,
            ),
        )

        conn.commit()
        conn.close()

        return candidate_id

    def get_candidates(self, job_id: str) -> List[Dict]:
        """
        Get all candidates for a job.

        Parameters
        ----------
        job_id : str
            Job ID

        Returns
        -------
        List[Dict]
            List of candidates
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM candidates WHERE job_id = ? ORDER BY probability DESC", (job_id,))
        rows = cursor.fetchall()

        conn.close()

        candidates = []
        for row in rows:
            candidate = dict(row)
            candidate["flags"] = json.loads(candidate["flags"])
            candidate["plots"] = json.loads(candidate["plots"])
            candidates.append(candidate)

        return candidates


# Global job store instance
_job_store: Optional[JobStore] = None


def get_job_store(db_path: str = "resonant_worlds.db") -> JobStore:
    """
    Get or create global job store instance.

    Parameters
    ----------
    db_path : str
        Database path

    Returns
    -------
    JobStore
        Global job store
    """
    global _job_store

    if _job_store is None:
        _job_store = JobStore(db_path)

    return _job_store
