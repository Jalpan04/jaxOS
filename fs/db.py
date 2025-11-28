import sqlite3
import os
from typing import List, Optional, Tuple

DB_PATH = "system.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        """Initialize the database schema."""
        # Files Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                content TEXT,
                owner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Users Table (for Phase 4)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                recovery_key_hash TEXT NOT NULL,
                is_root BOOLEAN DEFAULT 0
            )
        """)

        # Config Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.conn.commit()

    def write_file(self, path: str, content: str, owner_id: Optional[int] = None) -> bool:
        """Create or update a file."""
        try:
            self.cursor.execute("""
                INSERT INTO files (path, content, owner_id)
                VALUES (?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    content = excluded.content,
                    updated_at = CURRENT_TIMESTAMP
            """, (path, content, owner_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB Error] write_file: {e}")
            return False

    def read_file(self, path: str) -> Optional[str]:
        """Read a file's content."""
        self.cursor.execute("SELECT content FROM files WHERE path = ?", (path,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        try:
            self.cursor.execute("DELETE FROM files WHERE path = ?", (path,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"[DB Error] delete_file: {e}")
            return False

    def list_files(self) -> List[str]:
        """List all file paths."""
        self.cursor.execute("SELECT path FROM files")
        return [row[0] for row in self.cursor.fetchall()]

    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        self.cursor.execute("SELECT 1 FROM files WHERE path = ?", (path,))
        return self.cursor.fetchone() is not None

    # --- User Management ---

    def create_user(self, username: str, password_hash: str, recovery_hash: str = "") -> bool:
        try:
            self.cursor.execute("""
                INSERT INTO users (username, password_hash, recovery_key_hash)
                VALUES (?, ?, ?)
            """, (username, password_hash, recovery_hash))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB Error] create_user: {e}")
            return False

    def get_user(self, username: str) -> Optional[Tuple[int, str, str, str]]:
        """Returns (id, username, password_hash, recovery_key_hash)"""
        self.cursor.execute("SELECT id, username, password_hash, recovery_key_hash FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def count_users(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def update_password(self, username: str, password_hash: str) -> bool:
        """Updates the password for a user."""
        try:
            self.cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"[DB Error] update_password: {e}")
            return False
