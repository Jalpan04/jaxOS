import hashlib
import secrets
from fs.db import Database

class AuthManager:
    def __init__(self, db: Database):
        self.db = db
        self.current_user = None

    def hash_password(self, password: str) -> str:
        """Returns SHA-256 hash of the password."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> bool:
        """Registers a new user."""
        if self.db.get_user(username):
            return False # User exists
        
        pw_hash = self.hash_password(password)
        # Generate a dummy recovery key for now (Phase 4.3 will implement real recovery)
        recovery_key = secrets.token_hex(8) 
        recovery_hash = self.hash_password(recovery_key)
        
        return self.db.create_user(username, pw_hash, recovery_hash)

    def login(self, username: str, password: str) -> bool:
        """Attempts to log in. Returns True on success."""
        user = self.db.get_user(username)
        if not user:
            return False
            
        # user = (id, username, password_hash, recovery_key_hash)
        stored_hash = user[2]
        if self.hash_password(password) == stored_hash:
            self.current_user = username
            return True
        return False

    def logout(self):
        self.current_user = None

    def has_users(self) -> bool:
        """Checks if any users exist in the system."""
        return self.db.count_users() > 0
