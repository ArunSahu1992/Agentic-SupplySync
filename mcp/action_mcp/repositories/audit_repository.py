"""Repository module for persistent storage of audit log records.

This module provides a thread-safe, append-only repository pattern for managing
audit logs on disk using the JSON Lines (JSONL) format.
"""

from pathlib import Path

# Standard library imports
import json
import os
import threading
from typing import Any, Dict, List


class AuditRepository:
    """Provides file-based persistent storage for audit records.

    This repository handles initial directory setup, thread-safe appending
    of new audit log entries, and retrieval of full log histories using the
    JSON Lines (.jsonl) format to maintain O(1) write operations.

    Attributes:
        file_path (Path): The resolved absolute path to the audit log file.
    """

    def __init__(self, file_path: str | Path) -> None:
        """Initializes the repository, creating necessary directories and target file.

        Args:
            file_path (str | Path): Path to the destination audit file (preferably `.jsonl`).

        Raises:
            OSError: If directory or file creation fails due to system permissions.
        """
        # Store resolved absolute path to ensure consistent operations across working dirs
        self.file_path: Path = Path(file_path).resolve()
        
        # In-process lock to ensure thread safety across concurrent execution contexts
        self._lock: threading.Lock = threading.Lock()

        # Ensure parent directory tree exists before file initialization
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Atomically initialize target file if missing (avoids race conditions)
        if not self.file_path.exists():
            self.file_path.touch(exist_ok=True)

    def save(self, audit_record: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a new audit record to the end of the audit log.

        Serializes the incoming dictionary payload to a compact single-line JSON text 
        and writes it in append mode (`a`). This ensures O(1) time complexity and avoids
        loading full file histories into memory.

        Args:
            audit_record (Dict[str, Any]): The key-value structured audit log payload.

        Returns:
            Dict[str, Any]: The saved audit record payload upon successful write.

        Raises:
            TypeError: If `audit_record` contains non-JSON-serializable data types.
            IOError: If writing to disk fails.
        """
        # Serialize dict to single-line JSON to conform with JSONL format
        json_line: str = json.dumps(audit_record, ensure_ascii=False) + "\n"

        # Acquire lock to prevent race conditions during multi-threaded file writes
        with self._lock:
            with open(self.file_path, mode="a", encoding="utf-8") as file:
                file.write(json_line)

        return audit_record

    def get_all(self) -> List[Dict[str, Any]]:
        """Reads and parses all audit records from disk.

        Returns:
            List[Dict[str, Any]]: List of parsed audit record dictionaries ordered chronologically.

        Raises:
            json.JSONDecodeError: If any line in the audit file contains invalid JSON.
            IOError: If reading the audit file fails.
        """
        if not self.file_path.exists():
            return []

        # Lock read operations to avoid reading while another thread is mid-write
        with self._lock:
            with open(self.file_path, mode="r", encoding="utf-8") as file:
                return [
                    json.loads(line) 
                    for line in file 
                    if line.strip()  # Ignore empty lines
                ]